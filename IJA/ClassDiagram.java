package ija.homework1.uml;

import java.lang.*;
import java.util.*;

public class ClassDiagram extends Element {

    List<UMLClass> UMLClassList = new ArrayList<UMLClass>();
    List<UMLClassifier> UMLClassifierList = new ArrayList<UMLClassifier>();

    public ClassDiagram(String name) {
        super(name);
    }

    public UMLClass createClass(String name){
            if (this.UMLClassList.stream().anyMatch(o -> o.getName().equals(name))){
                return null;
            } else {
                UMLClass newUMLClass = new UMLClass(name);
                this.UMLClassList.add(newUMLClass);
                this.UMLClassifierList.add(newUMLClass);
                return newUMLClass;
            }
    }

    public UMLClassifier classifierForName(String name){
        if (this.UMLClassifierList.stream().anyMatch(o -> o.getName().equals(name))){
            String targetClassifier = name;
            for (UMLClassifier item : this.UMLClassifierList) {
                if (targetClassifier.equals(item.getName())) {
                    return item;
                }
            }
        } else {
            UMLClassifier newUMLClassifier = UMLClassifier.forName(name);
            this.UMLClassifierList.add(newUMLClassifier);
            return newUMLClassifier;
        }
        return new UMLClassifier(name);
    }

    public UMLClassifier findClassifier(String name){
        if (this.UMLClassifierList.stream().anyMatch(o -> o.getName().equals(name))){
            String targetClassifier = name;
            for (UMLClassifier item : this.UMLClassifierList) {
                if (targetClassifier.equals(item.getName())) {
                    return item;
                }
            }
        }
        return null;
    }

}