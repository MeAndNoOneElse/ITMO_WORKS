package org.example;

import com.fastcgi.FCGIInterface;

public class Main {
  public static void main(String[] args) {
    System.setProperty("FCGI_PORT", "12346");
    FCGIInterface fcgiInterface = new FCGIInterface();
    ResponseSender sender = new ResponseSender();
    while (fcgiInterface.FCGIaccept() >= 0) {
      sender.sendResponse();
    }
  }
}