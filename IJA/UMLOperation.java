package ija.homework1.uml;

import java.lang.*;
import java.util.*;

public class UMLOperation extends UMLAttribute {

    List<UMLAttribute> argList = new ArrayList<UMLAttribute>();

    public UMLOperation (String name, UMLClassifier type) {
        super(name,type);
    }

    public boolean addArgument(UMLAttribute arg) {
        if (this.argList.contains(arg)) {
            return false;
        } else {
            this.argList.add(arg);
            return true;
        }
    }

    public static UMLOperation create(String name, UMLClassifier type, UMLAttribute... args){
        UMLOperation newOperation = new UMLOperation(name, type);
        newOperation.argList.addAll(Arrays.asList(args));
        return newOperation;

    }

    public List<UMLAttribute> getArguments() {
        return this.argList;
    }
}