package ija.homework1.uml;

import java.lang.*;
import java.util.*;

public class UMLClassifier extends Element {

    protected boolean isUserDefined;

    public UMLClassifier (String name) {
        super(name);
        this.isUserDefined = false;
    }
    public UMLClassifier (String name, boolean isUserDefined) {
        super(name);
        this.isUserDefined = isUserDefined;
    }

    public static UMLClassifier forName(String name) {
        return new UMLClassifier(name);
    }

    public boolean isUserDefined() {
        return this.isUserDefined;
    }

    @Override
    public String toString() {
        String s = this.name + "(" + this.isUserDefined + ")";
        return s;
    }

}