package enums;

public enum Actions {
    SEE("посмотрите"),
    LOOK("смотреть"),
    LOVE("любил"),
    WAS("было"),
    HURRY("спешил"),
    COMEBACK("вернуться"),
    STIKOUT("торчит"),
    EXIST("взялся"),
    BE("бы"),
    DEF("ничего не делает"),
    EAT("ест"),
    FILLED("наполнилась"),
    BECOME("становился"),
    ACTED("действовал"),
    REMEMBER("вспоминал"),
    OVERCAME("одолевала"),
    FORGOT("забывался"),
    ASLEEP("заснул"),
    DREAM("мерещились"),
    SEEMED("казалось"),
    DRESSES("одевала"),
    RUB("натирать"),
    MUST("должен"),
    ENTRUST("поручать"),
    THOUGHT("считала"),
    SLEEP("спит"),
    CHEW("разжевать"),
    DRINK("пьёт"),
    WORK("работа"),
    SERVE("служит"),
    TOOK("сняла"),
    READY("собралась"),
    AWAKE("бодорствует"),
    SAID("сказал"),
    PETRIFY("окаменело"),
    EXCLAIMED("воскликнула"),
    ASKED("спросил"),
    THINK("подумал"),
    RUNING("побежал");
    private String name;

    Actions(String var1) {
        this.name = var1;
    }

    @Override
    public String toString() {
        return name;
    }
}
