public class FluxCapacitor {

    private final double REQ_GIGA_WATTS = 1.21;
    public double currentGigaWats = 0;

    public FluxCapacitor() {}

      public double getWattDifference() {
        return REQ_GIGA_WATTS - currentGigaWats;
      }
}
