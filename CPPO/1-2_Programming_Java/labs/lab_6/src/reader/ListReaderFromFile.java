package reader;

import chek.Chek;
import chek.Generation;
import chek.exeptions.*;
import modules.*;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.w3c.dom.Node;
import org.w3c.dom.NodeList;
import org.xml.sax.InputSource;
import org.xml.sax.SAXException;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import javax.xml.parsers.ParserConfigurationException;
import java.io.FileReader;
import java.io.IOException;
import java.io.StringReader;
import java.text.ParseException;
import java.text.SimpleDateFormat;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Date;

import static modules.Collectionr.ticketList;

/**
 * @author Andrey Anufriev
 * Этот класс нужен для загрузки коллекции из файла
 */
public abstract class ListReaderFromFile implements Reader {
    //создаём дату последней загрузки (для info)
    private static Date initializationDate = new Date();
    public static Date getInitializationDate(){
        return initializationDate;
    }
    /**
     * Этот метод получает имя файла xml и загружает из него коллекцию
     * @param fileName
     * @throws IOException ParserConfigurationException, SAXException
     *
     */
    public static void  read(String fileName) throws IOException, ParserConfigurationException, SAXException {
        try (FileReader fileReader = new FileReader(fileName)) {
            // Читаем содержимое файла в строку
            StringBuilder xmlContent = new StringBuilder();
            int character;
            while ((character = fileReader.read()) != -1) {
                xmlContent.append((char) character);
            }
            // Создаем фабрику и парсер для XML
            DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
            DocumentBuilder builder = factory.newDocumentBuilder();

            // Читаем XML-файл
            Document document = builder.parse(new InputSource(new StringReader(xmlContent.toString())));

            // Получаем корневой элемент
            Element root = document.getDocumentElement();

            // Получаем список всех элементов <Ticket...>
            // Мы проходим по всем дочерним элементам корневого элемента,
            // используя getChildNodes().
            NodeList tickets = root.getChildNodes();
//
            // Проходим по каждому элементу <Ticket...>
            int collisionCount = 0;
            for (int i = 0; i < tickets.getLength(); i++) {
                Node ticketNode = tickets.item(i);

                // Проверяем, что это элемент (игнорируем текстовые узлы и другие)
                //ticketNode.getNodeType() — это метод, который возвращает тип текущего узла. Узлы в XML могут быть разных типов, например:
                //Node.ELEMENT_NODE — узел является элементом (например, <Ticket12365478963214587>).
                //Node.TEXT_NODE — узел является текстовым содержимым (например, пробелы или текст между тегами).
                //Node.COMMENT_NODE — узел является комментарием.
                //В данном случае мы проверяем, является ли узел элементом (ELEMENT_NODE).
                // Это нужно, чтобы игнорировать текстовые узлы (например, пробелы или переносы строк),
                // которые могут находиться между элементами.

                if (ticketNode.getNodeType() == Node.ELEMENT_NODE) {
                    Element ticketElement = (Element) ticketNode;
                    try {
                        // Получаем значения <id> и добавляем его в множество LongID
                        long id;
                        if (Chek.IDlond(ticketElement.getElementsByTagName("id").item(0).getTextContent().trim())) {
                            id = Long.parseLong(ticketElement.getElementsByTagName("id").item(0).getTextContent().trim());
                            Generation.LongID.add(id);
                        } else {
                            throw new InvalidValueInXML("Неверное поле id в билете: " + ticketElement);
                        }


                        //получаем имя
                        String name;
                        if (Chek.name(ticketElement.getElementsByTagName("name").item(0).getTextContent().trim())) {
                            name = ticketElement.getElementsByTagName("name").item(0).getTextContent().trim();
                        } else {
                            throw new InvalidValueInXML("Неверное поле name в билете: " + ticketElement);
                        }


                        // получаем цену
                        int price;
                        if (Chek.price(ticketElement.getElementsByTagName("price").item(0).getTextContent().trim())) {
                            price = Integer.parseInt(ticketElement.getElementsByTagName("price").item(0).getTextContent().trim());
                        } else {
                            throw new InvalidValueInXML("Неверное поле price в билете: " + ticketElement);
                        }


                        // получаем комментарии Может быть null
                        String comment = null;
                        if (ticketElement.getElementsByTagName("comment").getLength() > 0) {
                            comment = ticketElement.getElementsByTagName("comment").item(0).getTextContent().trim();
                        }
                        // получаем координаты x y
                        Element coordinatesElement = (Element) ticketElement.getElementsByTagName("coordinates").item(0);
                        double x;
                        if (Chek.coordinateX(coordinatesElement.getElementsByTagName("X").item(0).getTextContent().trim())) {
                            x = Double.parseDouble(coordinatesElement.getElementsByTagName("X").item(0).getTextContent().trim());
                        } else {
                            throw new InvalidValueInXML("Неверное поле coordinateX в билете: " + ticketElement);
                        }

                        float y;
                        if (Chek.coordinateY(coordinatesElement.getElementsByTagName("Y").item(0).getTextContent().trim())) {
                            y = Float.parseFloat(coordinatesElement.getElementsByTagName("Y").item(0).getTextContent().trim());
                        } else {
                            throw new InvalidValueInXML("Неверное поле coordinateY в билете: " + ticketElement);
                        }

                        Coordinates coordinates = new Coordinates(x, y);

                        //Делаем дату  2025-02-10T19:00:00.367928500
                        String strCreateData = ticketElement.getElementsByTagName("creationDate").item(0).getTextContent().trim();
                        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd'T'HH:mm:ss.nnnnnn");
                        LocalDateTime createData = LocalDateTime.parse(strCreateData, formatter);

                        //Делаем тип билета может быть null
                        TicketType type = null;

                        if (ticketElement.getElementsByTagName("type").getLength() > 0) {
                            if (Chek.ticketType(ticketElement.getElementsByTagName("type").item(0).getTextContent().trim())) {
                                String typeString = ticketElement.getElementsByTagName("type").item(0).getTextContent().trim();
                                type = TicketType.valueOf(typeString); // Преобразуем строку в TicketType
                            } else {
                                throw new InvalidValueInXML("Неверное поле ticketType в билете: " + ticketElement);
                            }

                        }
                        //Делаем ивент (Int id, String name, java.util.Date date, EventType eventType)
                        Event event = null;
                        if (ticketElement.getElementsByTagName("event").getLength() > 0) {

                            Element eventElement = (Element) ticketElement.getElementsByTagName("event").item(0);
                            int idEvent;
                            if (Chek.IDint(eventElement.getElementsByTagName("idEvent").item(0).getTextContent().trim())) {
                                idEvent = Integer.parseInt(eventElement.getElementsByTagName("idEvent").item(0).getTextContent().trim());
                                Generation.IntID.add(idEvent);
                            } else {
                                throw new InvalidValueInXML("Неверное поле idEvent в билете: " + ticketElement);
                            }
                            String nameEvent;
                            if (Chek.name(eventElement.getElementsByTagName("nameEvent").item(0).getTextContent().trim())) {
                                nameEvent = eventElement.getElementsByTagName("nameEvent").item(0).getTextContent().trim();
                            } else {
                                throw new InvalidValueInXML("Неверное поле nameEvent в билете: " + ticketElement);
                            }

                            // Обрабатываем дату события (может быть null) yyyy.MM.dd.HH.mm
                            java.util.Date date = null;
                            if (eventElement.getElementsByTagName("date").getLength() > 0) {
                                String dateString;
                                if (Chek.dateEventInFile(eventElement.getElementsByTagName("date").item(0).getTextContent().trim())) {
                                    dateString = eventElement.getElementsByTagName("date").item(0).getTextContent().trim();
                                    SimpleDateFormat format = new SimpleDateFormat("yyyy.MM.dd.HH.mm");
                                    try {
                                        // Парсинг строки в Date
                                        date = format.parse(dateString);
                                    } catch (ParseException e) {
                                        throw new InvalidDate("неверный формат даты");
                                    }
                                }
                            } else {
                                throw new InvalidValueInXML("Неверное поле date в билете: " + ticketElement);
                            }

                            // Обрабатываем тип события (может быть null)
                            EventType eventType = null;
                            if (eventElement.getElementsByTagName("EventType").getLength() > 0) {
                                if (Chek.EventType(eventElement.getElementsByTagName("EventType").item(0).getTextContent().trim())) {
                                    eventType = EventType.fromValue(eventElement.getElementsByTagName("EventType").item(0).getTextContent().trim());
                                } else {
                                    throw new InvalidValueInXML("Неверное поле EventType в билете: " + ticketElement);
                                }

                            }
                            event = new Event(idEvent, nameEvent, date, eventType);
                        }
                        //Создаём Ticket и добавляем его в коллекцию
                        Ticket ticket = new Ticket(id, name, coordinates, createData, price, comment, type, event);
                        ticketList.add(ticket);

                    }
                    catch (Exception e){
                        collisionCount++;
                        continue;

                    }
                }
            }
            System.out.println("Пропущено "+collisionCount+" билетов.\nЗагрузка произведена из файла: "+fileName);
        } catch (Exception e) {
            e.printStackTrace();
            System.out.println("Ошибка при чтении файла");
        }
    }
}
