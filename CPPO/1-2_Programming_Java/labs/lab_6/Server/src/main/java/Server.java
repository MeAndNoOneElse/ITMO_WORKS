import java.io.*;
import java.net.ServerSocket;
import java.net.Socket;

public class Server {
    public static void main(String[] args) {
        try (ServerSocket serverSocket = new ServerSocket(8888)) {
            System.out.println("Сервер запущен. Ожидание клиентов...");

            while (true) {
                try (Socket clientSocket = serverSocket.accept();
                     ObjectInputStream ois = new ObjectInputStream(clientSocket.getInputStream());
                     ObjectOutputStream oos = new ObjectOutputStream(clientSocket.getOutputStream())) {

                    Message request = (Message) ois.readObject();
                    System.out.println("Получено: " + request);

                    Message response = new Message("Server", "Ответ на: " + request.getContent());
                    oos.writeObject(response);

                } catch (IOException | ClassNotFoundException e) {
                    System.err.println("Ошибка обработки клиента: " + e.getMessage());
                }
            }
        } catch (IOException e) {
            System.err.println("Сервер упал: " + e.getMessage());
        }
    }
}