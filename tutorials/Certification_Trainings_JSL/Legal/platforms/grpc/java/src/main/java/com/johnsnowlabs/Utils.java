package com.johnsnowlabs;

import java.util.*;
import java.nio.charset.*;

public class Utils {
    public static int NUM_WORKERS = 3;
    public static int RANGE_START = 8000;
    public static String PARAGRAPH = "Indemnification. 4.1.1 The Company agrees to indemnify, to the extent permitted by law, each Holder of Registrable Securities, its officers and directors and each person who controls such Holder (within the meaning of the Securities Act) against all losses, claims, damages, liabilities and expenses (including attorneys’ fees) caused by any untrue or alleged untrue statement of material fact contained in any Registration Statement, Prospectus or preliminary Prospectus or any amendment thereof or supplement thereto or any omission or alleged omission of a material fact required to be stated therein or necessary to make the statements therein not misleading, except insofar as the same are caused by or contained in any information furnished in writing to the Company by such Holder expressly for use therein. The Company shall indemnify the Underwriters, their officers and directors and each person who controls such Underwriters (within the meaning of the Securities Act) to the same extent as provided in the foregoing with respect to the indemnification of the Holder.";

    public static String DOCUMENT = String.join("\n", Collections.nCopies(25, PARAGRAPH));

}
