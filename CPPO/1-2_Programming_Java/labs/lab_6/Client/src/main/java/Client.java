import java.io.*;
import java.net.InetSocketAddress;
import java.nio.ByteBuffer;
import java.nio.channels.SocketChannel;
import java.util.concurrent.TimeUnit;

public class Client {
    private static final int MAX_RETRIES = 3;
    private static final int RETRY_DELAY_MS = 2000;

    public static void main(String[] args) {
        for (int attempt = 1; attempt <= MAX_RETRIES; attempt++) {
            try {
                connectToServer();
                break; // Успешное подключение
            } catch (IOException e) {
                System.err.println("Попытка " + attempt + " неудачна: " + e.getMessage());
                if (attempt == MAX_RETRIES) {
                    System.err.println("Сервер недоступен после " + MAX_RETRIES + " попыток.");
                    return;
                }
                try {
                    TimeUnit.MILLISECONDS.sleep(RETRY_DELAY_MS);
                } catch (InterruptedException ie) {
                    Thread.currentThread().interrupt();
                }
            }
        }
    }

    private static void connectToServer() throws IOException {
        try (SocketChannel channel = SocketChannel.open()) {
            channel.configureBlocking(false); // Неблокирующий режим
            channel.connect(new InetSocketAddress("localhost", 8888));

            // Ждём подключения с таймаутом
            long timeout = 5000; // 5 секунд
            long startTime = System.currentTimeMillis();
            while (!channel.finishConnect()) {
                if (System.currentTimeMillis() - startTime > timeout) {
                    throw new IOException("Таймаут подключения");
                }
                Thread.yield();
            }

            // Обмен данными
            ByteBuffer buffer = ByteBuffer.allocate(1024);
            Message message = new Message("Client", "Ping");

            // Сериализация сообщения
            ByteArrayOutputStream baos = new ByteArrayOutputStream();
            ObjectOutputStream oos = new ObjectOutputStream(baos);
            oos.writeObject(message);
            oos.flush();
            byte[] data = baos.toByteArray();

            // Отправка
            buffer.put(data);
            buffer.flip();
            while (buffer.hasRemaining()) {
                channel.write(buffer);
            }

            // Получение ответа
            buffer.clear();
            while (channel.read(buffer) == 0) {
                Thread.yield(); // Неблокирующее ожидание
            }
            buffer.flip();
            byte[] responseData = new byte[buffer.remaining()];
            buffer.get(responseData);

            // Десериализация
            ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(responseData));
            Message response = (Message) ois.readObject();
            System.out.println("Ответ сервера: " + response);

        } catch (ClassNotFoundException e) {
            throw new IOException("Ошибка десериализации", e);
        }
    }
}