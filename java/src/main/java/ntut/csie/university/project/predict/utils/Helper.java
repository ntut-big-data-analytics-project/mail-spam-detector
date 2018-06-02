package ntut.csie.university.project.predict.utils;

import com.google.common.io.ByteStreams;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.io.*;
import java.nio.charset.Charset;
import java.util.Properties;

public final class Helper {
    private Helper() {
    }

    public static long getUnixTimeStamp() {
        return System.currentTimeMillis() / 1000L;
    }

    public static String padLeft(String str, int len) {
        return padLeft(str, len, " ");
    }

    public static String padLeft(String str, int len, String paddingStr) {
        StringBuilder sb = new StringBuilder();
        for (int toPrepend = (int) Math.ceil(len - str.length() / paddingStr.length()); toPrepend > 0; toPrepend--) {
            sb.append(paddingStr);
        }
        sb.append(str);

        return sb.toString();
    }

    public static String toJSON(Object obj) {
        return toJSON(obj, obj.getClass());
    }

    public static <T> String toJSON(Object obj, Class<T> model) {
        Gson gson = new GsonBuilder().create();
        return gson.toJson(obj, model);
    }

    public static Object parseJSON(String jsonStr, Class c) {
        Gson gson = new GsonBuilder().create();
        return gson.fromJson(jsonStr, c.getClass());
    }


    public static byte[] streamToBytes(InputStream is) {
        ByteArrayOutputStream outStream = new ByteArrayOutputStream();
        final int BUFFER_SIZE = 8192;
        byte[] data = new byte[BUFFER_SIZE];
        int count = -1;
        try {
            while ((count = is.read(data, 0, BUFFER_SIZE)) != -1)
                outStream.write(data, 0, count);
        } catch (IOException e) {
            e.printStackTrace();
        }

        return outStream.toByteArray();
    }

    public static String streamToString(InputStream is) {
        final byte[] data = streamToBytes(is);

        try {
            return new String(data, "UTF-8");
        } catch (UnsupportedEncodingException e) {
            return "";
        }
    }

    public static String readFileAsString(File f, Charset c) throws IOException {
        FileInputStream fis = new FileInputStream(f);
        byte[] data = streamToBytes(fis);
        fis.close();
        return new String(data, c);
    }


    public static class Pair<L, R> {
        private final L left;
        private final R right;

        public Pair(L left, R right) {
            this.left = left;
            this.right = right;
        }

        public L getLeft() {
            return left;
        }

        public R getRight() {
            return right;
        }

        @Override
        public int hashCode() {
            return left.hashCode() ^ right.hashCode();
        }

        @Override
        public boolean equals(Object o) {
            if (!(o instanceof Pair)) return false;
            Pair pairo = (Pair) o;
            return this.left.equals(pairo.getLeft()) &&
                    this.right.equals(pairo.getRight());
        }

    }

    public static String getExtension(File file) {
        return getExtension(file.getName());
    }

    public static String getExtension(String fileName) {
        char ch;
        int len;
        if (fileName == null ||
                (len = fileName.length()) == 0 ||
                (ch = fileName.charAt(len - 1)) == '/' || ch == '\\' || //in the case of a directory
                ch == '.') //in the case of . or ..
            return "";
        int dotInd = fileName.lastIndexOf('.'),
                sepInd = Math.max(fileName.lastIndexOf('/'), fileName.lastIndexOf('\\'));
        if (dotInd <= sepInd)
            return "";
        else
            return fileName.substring(dotInd + 1).toLowerCase();
    }

    public static InputStream getResourceAsStream(String name) throws IOException {
        return ClassLoader.getSystemClassLoader().getResourceAsStream(name);
    }

    public static byte[] getResourceAsByte(String name) throws IOException {
        InputStream is = getResourceAsStream(name);
        return ByteStreams.toByteArray(is);
    }

    public static long gcd(long m, long n) {
        long r = 0;
        while (n != 0) {
            r = m % n;
            m = n;
            n = r;
        }

        return m;
    }

    public static long gcd(long m, long n, long... vArr) {
        long ret = gcd(m, n);
        for (long v : vArr) {
            ret = gcd(ret, v);
        }
        return ret;
    }
}
