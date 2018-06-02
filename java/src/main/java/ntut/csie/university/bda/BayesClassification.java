package ntut.csie.university.bda;

import ntut.csie.university.project.predict.WebServer;
import ntut.csie.university.project.predict.utils.Helper;
import okhttp3.*;
import org.apache.commons.io.FileUtils;
import org.apache.spark.api.java.JavaRDD;
import org.apache.spark.api.java.JavaSparkContext;
import org.apache.spark.mllib.classification.NaiveBayes;
import org.apache.spark.mllib.classification.NaiveBayesModel;
import org.apache.spark.mllib.feature.HashingTF;
import org.apache.spark.mllib.feature.IDF;
import org.apache.spark.mllib.feature.IDFModel;
import org.apache.spark.mllib.linalg.Vector;
import org.apache.spark.mllib.regression.LabeledPoint;
import org.apache.spark.sql.SQLContext;
import org.apache.spark.sql.SparkSession;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;
import java.util.stream.Collectors;

public class BayesClassification {
    private static final String SP_CHAR = Pattern.quote("/ ");
    private static final String PYTHON_SPLIT_SERVER = "http://127.0.0.1:4123/process-email";
    private static final boolean FROM_LOAD = false;
    private static final boolean INCLUDE_TF_IDF = true;

    public static void main(String[] args) throws Exception {

        if (args.length != 2) {
            System.err.println("Usage: BayesClassification <spamPath> <hamPath>");
            System.exit(1);
        }

        final SparkSession spark = SparkSession
                .builder()
                .appName("Bayes_classification")
                .getOrCreate();

        final JavaSparkContext sc = new JavaSparkContext(spark.sparkContext());
        final SQLContext sqlCxt = SQLContext.getOrCreate(sc.sc());
        final File savePath = new File("Y:/NaiveBayesModel");
        final HashingTF tf = new HashingTF();
        final IDFModel idf;
        final NaiveBayesModel model;
        final File idfSerFile = Paths.get(savePath.getAbsolutePath(), "idf.jserialized").toFile();
        final File modelFile = Paths.get(savePath.getAbsolutePath(), "model").toFile();

        tf.setHashAlgorithm("native");
        if (!FROM_LOAD) {
            final List<Path> spamList = getAllFilesInPath(new File(args[0]).toPath());
            final List<Path> hamList = getAllFilesInPath(new File(args[1]).toPath());


            final JavaRDD<Vector> spamFeatures;
            final JavaRDD<Vector> hamFeatures;
            {
                final JavaRDD<Vector> spamWords = getWordsHash(sc, tf, spamList);
                final JavaRDD<Vector> hamWords = getWordsHash(sc, tf, hamList);
                if (INCLUDE_TF_IDF) {
                    final JavaRDD<Vector> dataSetVector = spamWords.union(hamWords);
                    dataSetVector.cache();
                    idf = new IDF().fit(dataSetVector.rdd());
                    spamFeatures = spamWords.map(idf::transform);
                    hamFeatures = hamWords.map(idf::transform);
                } else {
                    idf = null;
                    spamFeatures = spamWords;
                    hamFeatures = hamWords;
                }
            }

            final JavaRDD<LabeledPoint> posExample = spamFeatures.map(f -> new LabeledPoint(1, f));
            final JavaRDD<LabeledPoint> negExample = hamFeatures.map(f -> new LabeledPoint(0, f));

            final JavaRDD<LabeledPoint> dataSet = posExample.union(negExample);

            //fit model
            model = NaiveBayes.train(dataSet.rdd(), 1);

            if (savePath.exists()) FileUtils.deleteDirectory(savePath);
            model.save(sc.sc(), modelFile.getAbsolutePath());

            if (idf != null) {
                try (FileOutputStream idfFwr = new FileOutputStream(idfSerFile.getAbsolutePath())) {
                    try (ObjectOutputStream objWr = new ObjectOutputStream(idfFwr)) {
                        objWr.writeObject(idf);
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
//
//        // predict
//        //model.predict()
//            final long testSetCount = testSet.count();
//            final long tp = testSet.mapToPair(x -> new Tuple2<>(model.predict(x.features()), x.label())).filter(x -> x._1.equals(x._2)).count();
//            System.out.println(String.format("Model accuracy: %.2f", (double) tp / testSetCount));
        } else {
            Object tmpObj = null;
            try (FileInputStream fis = new FileInputStream(idfSerFile)) {
                try (ObjectInputStream ois = new ObjectInputStream(fis)) {
                    tmpObj = ois.readObject();
                }
            } catch (IOException e) {
                e.printStackTrace();
            }
            idf = (IDFModel) tmpObj;

            model = NaiveBayesModel.load(sc.sc(), modelFile.getAbsolutePath());
        }


        WebServer _server = WebServer.getInstance(7788);

        final OkHttpClient okHttpClient = new OkHttpClient.Builder()
                .connectTimeout(2, TimeUnit.SECONDS)
                .readTimeout(10, TimeUnit.SECONDS)
                .build();
        _server.addRoute("/bayes-test", new WebServer.WebServerResponse() {
            @Override
            protected byte[] response() throws Exception {
                String body = Helper.streamToString(httpExchange.getRequestBody());
                String[] data = body.split(SP_CHAR);
                Vector v = tf.transform(Arrays.asList(data));

                if (INCLUDE_TF_IDF) {
                    v = idf.transform(v);
                }

                double ret = model.predict(v);

                return String.valueOf((int) ret).getBytes();
            }
        });
        _server.addRoute("/bayes", new WebServer.WebServerResponse() {
            @Override
            protected byte[] response() throws Exception {
                String mailData = Helper.streamToString(httpExchange.getRequestBody());
                final RequestBody requestBody = RequestBody.create(MediaType.parse("message/rfc822"), mailData);
                final Request request = new Request.Builder()
                        .url(PYTHON_SPLIT_SERVER)
                        .method("POST", requestBody)
                        .build();
                final Response response = okHttpClient.newCall(request).execute();
                String body = new String(response.body().bytes(), StandardCharsets.UTF_8);

                String[] data = body.split(SP_CHAR);
                Vector v = tf.transform(Arrays.asList(data));

                if (INCLUDE_TF_IDF) {
                    v = idf.transform(v);
                }

                double ret = model.predict(v);
                return String.valueOf((int) ret).getBytes();
            }
        });

        _server.start();
        //spark.stop();
    }

    private static List<Path> getAllFilesInPath(Path path) throws IOException {
        return Files.walk(path).filter(Files::isRegularFile).collect(Collectors.toList());
    }

    private static JavaRDD<String> convertPathListToRdd(final JavaSparkContext sc, final List<Path> paths) {
        final List<JavaRDD<String>> fileRdd = paths.parallelStream()
                .map(
                        p -> sc.textFile(p.toAbsolutePath().toString())
                )
                .collect(Collectors.toList());
        return sc.union(sc.parallelize(new LinkedList<>()), fileRdd);
    }

    private static JavaRDD<Vector> getWordsHash(final JavaSparkContext sc, final HashingTF tf, final List<Path> list) {
        final List<Vector> l = list.parallelStream().flatMap(path -> {
            try {
                return Files.lines(path, StandardCharsets.UTF_8).parallel().map(s -> tf.transform(Arrays.asList(s.split(SP_CHAR))));
            } catch (IOException e) {
                e.printStackTrace();
                // return new LinkedList<>().stream();
                return null;
            }
        }).collect(Collectors.toList());

        return sc.parallelize(l);
    }

    private static JavaRDD<Vector> getFeatures(final HashingTF tf, final JavaRDD<String> src) {
        return src.map(s -> tf.transform(Arrays.asList(s.split(SP_CHAR))));
    }
}
