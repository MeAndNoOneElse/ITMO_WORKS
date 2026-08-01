package Character;

import enums.*;
import exeptions.NoItem;

public class MainCharacter extends Characters {
    public String name;
    public String appearance;
    public String location;
    public Actions stat;
    public Type type;

    public MainCharacter(String var1, String var2, String var3) {
        this.name = var1;
        this.appearance = var2;
        this.stat = Actions.DEF;
        this.location = var3;
        this.type = Type.BOY;
    }

    @Override
    public void say() {
        System.out.println("привет, меня зовут " + name + ". Я главный герой");
    }

    public String run(Object var1, Object var2) {
        return (var1 + " " + Actions.RUNING + " " + Actions.BE + " " + Phrases.FOR + " " + var2);
    }

    public String love(Object var1, Object var2, Object var3, Object var4, Object var5) {
        return (var1 + " " + Actions.LOVE + " " + var2 + " " + Phrases.ON + " " + var3 + " " + Sign.COMMA + " " + var4 + " " + Phrases.AND + " " + Phrases.ON + " " + var5);
    }

    public String hurry(Object var1, Object var2, Object var3) {
        return (var1 + " " + Actions.HURRY + " " + var2 + " " + Phrases.X13 + " " + var3);
    }

    public String eat(Object what) {
        return (name + " доедал " + what);
    }

    public String action(Object verb, Object verb2, Object dop) {
        return (getName(1) + " " + verb + ", что " + getName(2) + " пора " + verb2 + " к " + dop);
    }

    public String action(Object verb, Object dop) {
        return (getName(3) + " снова " + verb + " сильная " + dop);
    }

    public String forget() {
        return (getName(1) + " " + Actions.FORGOT);
    }

    public String sleep(Object who, Object var2) {
        return ("крепко " + Actions.ASLEEP + " " + who + " диване у " + var2);

    }

    public String sleep(Object var1, Object var2, Object var3) {
        return (getName(2) + " " + var1 + " " + var2 + " " + var3);
    }

    public String seemed() {
        return (getName(2) + " " + Actions.SEEMED + " будто ");
    }

    public void setStat(Actions stat) {
        this.stat = stat;
    }

    public String getStat() {
        return name + " " + stat;
    }

    public String live(Object var1, Object var2, Object var3) {
        return getName(1) + " жил вместе с " + var1 + " и " + var2 + ", которые оказались очень благовоспитанными особами, и вместе с ними прислуживал " + var3;
    }

    public String assigned(Object var) {
        return "Сначала " + getName(2) + " поручали только чистку сапог, " + getName(1) + " " + Actions.MUST + " был " + Actions.RUB + " до блеска маслом кокосовые скорлупки, служившие " + var + " туфлями";
    }

    public String entrust(Object var1) {
        return getName(2) + " стали " + Actions.ENTRUST + " более тонкую " + var1;
    }

    public String catching(Object var1, Object var2) {
        return "Вместе с несколькими другими " + var2 + " " + getName(1) + " " + Actions.MUST + " был ловить и собирать " + var1;
    }

    public String sift(Object var) {
        return "потом просеивать их сквозь тончайшее волосяное " + var;
    }

    public String transfer(Object var) {
        return (getName(0) + "был переведен в разряд" + var);
    }

    public String gather(Object var) {
        return ("собирали воду для питья " + var);
    }

    public String gather(Object var1, Object var2) {
        return (var1 + " и " + var2 + " должны были собирать в ореховые скорлупки росу с роз");
    }

    public String work(Object var) {
        return (" у водоносов, в том числе и у " + name + " " + var + " была не лёгкая");
    }

    public String transfer(Object var, Object var2) {
        return name + "a перевели " + var + " " + var2;
    }

    public String entrust(Object var, Object var2) {
        return getName(2) + " поручено было содержать " + var + " чистоте " + var2;
    }

    public String wrap(Object var, Object var2, Object var3) {
        return name + " должен был обертывать " + var + " старым " + var2 + " и разъезжать таким образом по всем " + var3 + "м";
    }

    public String overcame(Object var) {
        return name + " прошел все " + var + ": поваренка, помощника, первого повара";
    }

    public String reached() {
        return "достиг такой ловкости и уменья во всем, что часто дивился самому себе.";
    }

    public String pluck(Object var) {
        return getName(1) + " ощипал " + var;
    }

    public String fill(Object var) {
        return getName(1) + " начинил её " + var;
    }

    public String fried() {
        return " и хорошенько зажарил";
    }

    public String turn(Object var, Object var2) {
        return getName(1) + " свернул " + var + " " + var2;
    }

    public String cook(Object var) {
        return name + " сварил " + var;
    }

    public String scraped(Object var) {
        return "соскоблил " + var;
    }

    public String tookOut(Object var) {
        return "вынул из курицы " + var;
    }

    public String see(Object var0, String var) {
        return var0 + " " + getName(1) + " увидел " + var;
    }

    public String looked(Object var) {
        return getName(1) + " заглянул " + var;
    }

    public String open(Object var) {
        return name + " открыл " + var;
    }

    public String find(Object var1) {
        return "нашел в ней " + var1;
    }

    public String look(Object var) {
        return name + " задумчиво посмотрел на этот " + var;
    }

    public String sniffed() {
        return "понюхал его";
    }

    public String remember(Object var) {
        return name + " вспомнил, что он так же сильно пахнет, как тот суп, которым когда-то угостила его " + var;
    }

    public String sneeze() {
        return name + " начал так сильно чихать";
    }

    public String getup() {
        return " проснулся";
    }

    public String lay(Object var) {
        return getName(1) + " лежал на " + var;
    }

    public String lookaround() {
        return "осматривался кругом";
    }

    public String said(Object var) {
        return var + "";
    }

    public String rose(Object var) {
        return name + " поднялся с места, чтобы уйти " + var + "ой";
    }

    public String turNot(Object var) {
        return getName(1) + " не мог повернуть " + var;
    }

    public String laugh() {
        return getName(1) + " невольно рассмеялся над собой и  своей сонливостью";
    }

    public String knock(Object var) {
        return "каждую минуту стукался " + var + " то о шкаф, то о стену, то о косяк двери";
    }

    public String thing(Object var) {
        return "думал он, где-нибудь поблизости показывают " + var;
    }

    public String heard(Object var) {
        return getName(1) + " поминутно слышал " + var;
    }

    public String came(Object var) {
        return getName(2) + " стало как-то жутко, когда он пришел на " + var;
    }

    public String sleeped() {
        return "он проспал недолго";
    }

    public String cameUp(Object var) {
        return name + " подошёл к " + var + " сзади";
    }

    public String lowered(Object var, Object var2) {
        return "ласково опустил " + var + " на её " + var2;
    }

    public String decided(Object var) {
        return name + " решил отравить " + var;
    }

    public String added() {
        return getName(1) + " подсыпал в блюдо отраву";
    }

    public String tiered() throws NoItem {
        if (stat != Actions.SLEEP) {
            throw new NoItem();
        } else {
            return getName(1) + " умер и от этого проснулся";
        }
    }

    public String getName(Integer x) {
        return switch (x) {
            case 1 -> "он";
            case 2 -> "ему";
            case 3 -> "его";
            case 4 -> "него";
            default -> name;
        };
    }


    @Override
    public void action() {

    }

}
