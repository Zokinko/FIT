package ija.homework1.uml;

import java.lang.*;
import java.util.*;

public class Element extends Object {

    protected String name;

    public Element (String name) {
        this.name = name;
    }

    public String getName() {
        return this.name;
    }

    public void rename(String newName) {
        this.name = newName;
    }

}