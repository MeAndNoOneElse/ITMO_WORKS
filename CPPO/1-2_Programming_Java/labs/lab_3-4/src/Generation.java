import Character.*;
import enums.*;
import exeptions.NoItem;

import java.util.ArrayList;

public class Generation {
    public static void main(String[] args) {
        ArrayList<String> Adj = new ArrayList<>();
        ArrayList<String> W = new ArrayList<>();
        Adj.add(0, "пустой");
        Adj.add(1, "голубоватым");
        Adj.add(2, "серый");
        Adj.add(3, "гуще и гуще");
        Adj.add(4, "усыпительно");
        Adj.add(5, "сильная");
        Adj.add(6, "крепко");
        Adj.add(7, "странные");
        Adj.add(8, "бельчью");
        Adj.add(9, "огорчнный");
        W.add(0, "дым");
        W.add(1, "запах ладана");
        W.add(2, "дремота");
        W.add(3, "сны");
        W.add(4, "работу");
        W.add(5, "пылинки");
        W.add(6, "сито");
        W.add(7, "веществами");
        W.add(8, "зубов");
        W.add(9, "слуг");
        W.add(10, "домашние работы");
        W.add(11, "пол");
        W.add(12, "сукном");
        W.add(13, "степени");
        W.add(14, "туфли");
        W.add(15, "корзину");
        W.add(16, "цветок");
        W.add(17, "возгласы");

        Location Haus = new Location("Дом");
        Location Def = new Location("нигде");
        Location Room = new Location("комната");
        Location Kitchen = new Location("кухню");
        Location Storehouse = new Location("кладовой");
        Location Street = new Location("улица");
        Location Town = new Location("город");
        Location Market = new Location("рынок");

        Narrator P = new Narrator();
        MainCharacter Jacob = new MainCharacter("Яков", "Красивый", Def.name());
        Dwarf Karl = new Dwarf("Карл", 2, "безобразный ", Type.DWARF);
        Group Crowd = new Group("простолюдины", Type.CROWD);
        Group Curiosities = new Group("всякие диковинки");
        Giant Big = new Giant("Гоша", Type.GIANT);
        MC_Mum Mum = new MC_Mum("матери");
        Group Nobody = new Group("");
        GuineaPigs SeaPigs = new GuineaPigs("Коко и Шики", Type.PIGS);
        OldWomen OWumen = new OldWomen("Маргерет", Type.OLDWOMAN);
        Squirrel Squirrel = new Squirrel("ыпавр", Type.SQUIRREL);
        Chicken Chicken = new Chicken("кура");
        //1 предложение
        P.say(Phrases.UNTIL, Jacob.eat("последние ложки лакомого блюда"), Sign.COMMA, SeaPigs.action("аравийский ладан"), Sign.COMMA, Room.filled(Adj.get(2), "дымом"), Sign.DOT);
        Jacob.setStat(Actions.EAT);
        P.say(Jacob.name, Jacob.getStat(), Sign.DOT);
        //2 предложение
        P.say(W.get(0), Actions.BECOME, Adj.get(3), Sign.COMMA, Phrases.A, W.get(1), Adj.get(4), Actions.ACTED, Phrases.ON, Jacob.type, Sign.DOT);
        //3 предложение
        P.say(Phrases.SOMETIMES, Jacob.action(Actions.REMEMBER, Actions.COMEBACK, Mum.getName(1)), Sign.COMMA, Phrases.BUT, Phrases.X17, Jacob.action(Actions.OVERCAME, W.get(2)), Sign.DASH, Jacob.forget(), Phrases.AND, Jacob.sleep(Phrases.ON, OWumen.getType()), Sign.DOT);
        Jacob.setStat(Actions.SLEEP);
        P.say(Jacob.name, Jacob.getStat(), Sign.DOT);
        //4 предложение
        P.say(Jacob.sleep(Actions.DREAM, Adject.STRANGE, W.get(3)), Sign.DOT);
        //5 предложение начало сна
        P.say(Jacob.seemed(), OWumen.removes(Jacob.getName(4)), Phrases.AND, OWumen.dress(), Sign.DOT);
        //6 предложение
        P.say(Jacob.live(Squirrel.getType(), SeaPigs.getType(), OWumen.getType()), Sign.DOT);
        //7 предложение
        P.say(Jacob.assigned(OWumen.getType()), Sign.DOT);
        //8 предложение первый год
        P.say(Phrases.X18, Sign.DOT);
        //9 предложение
        P.say(Jacob.entrust(W.get(4)), Sign.DOT);
        //10 предложение
        P.say(Jacob.catching(W.get(5), Squirrel.getType()), Sign.COMMA, Phrases.A, Jacob.sift(W.get(6)), Sign.DOT);
        //11 предложение
        P.say(Phrases.X25, OWumen.thought(W.get(5), W.get(7)), Phrases.A, Phrases.X26, OWumen.hasNot(W.get(8)), Phrases.AND, OWumen.couldNot(Actions.CHEW), Phrases.THAT, Squirrel.bake(W.get(5)), Sign.DOT);
        //12 предложение второй год
        P.say(Phrases.X19, Sign.DOT);
        //13 предложение
        P.say(Jacob.transfer(W.get(9)), Sign.COMMA, Phrases.X27, Jacob.gather(OWumen.getType()), Sign.DOT);
        //14 предложение
        P.say(Jacob.gather(Squirrel.getType(), Jacob.name), Sign.DOT);
        P.say(OWumen.drink(OWumen.getType(), Actions.DRINK), Phrases.X28, Jacob.work(Actions.WORK), Sign.DOT);
        //15 предложение третий год
        P.say(Phrases.X19, Sign.DOT);
        //16 предложение
        P.say(Jacob.transfer(Phrases.ON, W.get(10)), Sign.DOT);
        //17 предложение
        P.say(Jacob.entrust(Phrases.IN, W.get(11)), Sign.COMMA, Phrases.BUT, Phrases.X26, Phrases.X29, Sign.DOT);
        //18 предложение
        P.say(Jacob.wrap(BodPar.FOOT, W.get(12), Room.name()), Sign.DOT);
        //19 предложение пятый год
        P.say(Phrases.X22, Jacob.transfer(Phrases.ON, Kitchen.name()), Sign.DOT);
        //20 предложение
        P.say(Jacob.overcame(W.get(13)), Sign.COMMA, Phrases.AND, Jacob.reached(), Sign.DOT);
        Jacob.setStat(Actions.SERVE);
        //21 предложение
        P.say(Phrases.X23, Sign.COMMA, Jacob.name, Jacob.getStat(), OWumen.getType(), Sign.DOT);
        //22 предложение
        P.say(Phrases.BUT, Phrases.X30, OWumen.took(Actions.TOOK, W.get(14), W.get(15)), Sign.COMMA, OWumen.leave(Actions.READY), Sign.DOT);
        //23 предложение
        P.say(OWumen.order(Jacob.name), Jacob.pluck(Chicken.getType()), Sign.COMMA, Jacob.fill("зеленью"), Phrases.AND, Jacob.fried(), Sign.DOT);
        //24 предложение
        P.say(Jacob.turn(Chicken.getType(), BodPar.NECK), Jacob.cook(Chicken.getName(3)), Jacob.pluck(BodPar.FEATHERS), Jacob.scraped(BodPar.LEATHER), Jacob.tookOut(BodPar.ENTRAILS), Sign.DOT);
        //25 предложение
        P.say(Phrases.IN, Jacob.see(Storehouse.name(), "шкафчик"), Sign.COMMA, Jacob.looked(Phrases.X31), Phrases.X32, Sign.DOT);
        //26 предложение
        P.say(Jacob.open(Phrases.X33), Phrases.AND, Jacob.find(Phrases.X34), Sign.DOT);
        //27 предложение
        P.say(Phrases.X35, Sign.DOT);
        //28 предложение
        P.say(Jacob.look(W.get(15)), Jacob.sniffed(), Phrases.AND, Jacob.remember(OWumen.getType()), Sign.DOT);
        if (Math.random() < 0.5) {
            Jacob.stat = Actions.SLEEP;

            P.say(Jacob.decided(OWumen.getName(6)), Sign.COMMA, Jacob.added(), Sign.COMMA, OWumen.cameBack(Haus.name()), Sign.DOT);
            P.say(OWumen.tiered(), Sign.DOT);
            P.say(Phrases.X46, Sign.DOT);
            P.say(Phrases.X47, Sign.DOT);
            P.say(Phrases.X48, Sign.DOT);
            try {
                P.say(Jacob.tiered(), Sign.DOT);
            } catch (NoItem e) {
                System.out.println("главный герой не может умереть");
            }
        } else {
            //29 предложение конец сна
            //29 предложение конец сна
            P.say(Jacob.sneeze(), Sign.COMMA, Phrases.X36, Jacob.getup(), Sign.DOT);
            Jacob.setStat(Actions.AWAKE);
            P.say(Jacob.getStat(), Sign.DOT);
        }
        //30 предложение
        P.say(Jacob.lay(Phrases.X37), Phrases.AND, Jacob.lookaround(), Sign.DOT);
        //31 предложение
        P.say(Jacob.said(Phrases.J1), Sign.DASH);
        P.say(Actions.SAID, Jacob.getName(1), Phrases.X38, Sign.COMMA);
        P.say(Jacob.said(Phrases.J2), Sign.EX);
        //32 предложение
        P.say(Jacob.said(Phrases.J3), Sign.EX);
        //33 предложение
        P.say(Phrases.X39, Jacob.rose(Haus.name()), Phrases.BUT, BodPar.ALL, Actions.PETRIFY, Phrases.X40, Jacob.turNot(BodPar.HEAD), Sign.DOT);
        //34 предложение
        P.say(Jacob.laugh(), Sign.COMMA, Phrases.X26, Jacob.knock(BodPar.NOSE), Sign.DOT);
        //35 предложение
        P.say(Squirrel.getType(), Phrases.AND, SeaPigs.getType(), Phrases.X41, Sign.DOT);
        //36 предложение
        P.say(Street.name(), OWumen.brought(Town.name()), Sign.DOT);
        //37 предложение
        P.say(Phrases.X42, Sign.EX);
        //38 предложение
        P.say(Phrases.X43, Sign.COMMA, Jacob.thing(Karl.getType()), Phrases.X26, Jacob.heard(W.get(17)), Sign.COLON);
        //39 предложение
        P.say(Phrases.OH, Sign.COMMA, P.action(1, "m", Karl.getDec(), Nobody.getName(), Actions.SEE, Phrases.ON, Adject.UGLY_I, Type.DWARF), Sign.EX);
        //40 предложение
        P.say(Phrases.WHERE, Karl.getName(), Actions.EXIST, Sign.QU);
        //41 предложение
        P.say(Phrases.WHICH, Phrases.AT, Karl.getName2(), Adject.LONG, BodPar.NOSE, Phrases.AND, Phrases.HOW, Adject.FUNNY, BodPar.HEAD, Actions.STIKOUT, Phrases.AT, Karl.getName2(), Adject.DIRECT, Phrases.ON, BodPar.SHOULDER, Sign.EX);
        //42 предложение
        P.say(Phrases.A, BodPar.HAND, Sign.DASH, Phrases.THAT, Sign.COMMA, BodPar.HAND, Phrases.X4, Phrases.AT, Karl.getName2(), Adject.BLACK, Sign.COMMA, Adject.UGLY, Sign.EX);
        //43 предложение
        P.say(Phrases.IN, Adject.OTHER, Phrases.TIME, Jacob.run(Jacob.getName(1), Crowd.getType()), Sign.COMMA, Phrases.BECAUSE, Adject.VERY, Jacob.love(Jacob.getName(1), Actions.LOOK, Big.getType(), Karl.getType(), Curiosities.getName()), Sign.COMMA, Phrases.BUT, Phrases.ON, Phrases.ONCE, Jacob.getName(2), Actions.WAS, Phrases.NOT, Phrases.TO, Phrases.X12, Sign.COLON, Jacob.hurry(Jacob.getName(1), Actions.COMEBACK, Mum.getName(1)), Sign.DOT);
        //44 предложение
        P.say(Jacob.came(Market.name()), Sign.DOT);
        //45 предложение
        P.say(Mum.sat(), Sign.COMMA, Phrases.BECAUSE, Jacob.sleeped(), Sign.DOT);
        //46 предложение
        P.say(Jacob.cameUp(Mum.getName(2)), Sign.COMMA, Jacob.lowered(BodPar.HAND, BodPar.SHOULDER), Phrases.AND, Actions.SAID, Sign.COLON);
        //47 предложение
        P.say(Jacob.said(Phrases.J4), Sign.QU);
        //48 предложение
        P.say(Mum.turn(), Sign.DOT);
        //49 предложение
        P.say(Mum.said(Phrases.M1), Sign.EX, Sign.DASH, Actions.EXCLAIMED, Mum.getName(1));
        //50 предложение
        P.say(Sign.DASH, Mum.said(Phrases.M2), Sign.EX);
        P.say(Jacob.said(Phrases.J5), Sign.QU, Actions.ASKED, Jacob.name, Phrases.X45, Sign.DOT);
        P.say(Sign.DASH, Jacob.said(Phrases.J6), Sign.COMMA, Jacob.said(Phrases.J7), Sign.QU);
        P.say(Mum.said(Phrases.M4), Sign.EX, Actions.SAID, Mum.getName(1), Phrases.X44, Sign.DOT);
        P.say(Sign.DASH, Mum.said(Phrases.M3), Sign.EX);
        P.say(Jacob.said(Phrases.J8), Sign.EX, Sign.DASH, Actions.THINK, Adj.get(9), Jacob.name, Sign.DOT);
        P.say(Jacob.said(Phrases.J9), Sign.QU);
    }
}
