package ija.homework1.uml;

import java.lang.*;
import java.util.*;

public class UMLAttribute extends Element {

    protected UMLClassifier type;

    public UMLAttribute (String name, UMLClassifier type) {
        super(name);
        this.type = type;
    }

    public UMLClassifier getType() {
        return this.type;
    }

    @Override
    public String toString() {
        String s = this.name + ":" + this.type;
        return s;
    }

}