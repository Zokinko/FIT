package ija.homework1.uml;

import java.lang.*;
import java.util.*;

public class UMLClass extends UMLClassifier {

    boolean isAbstract;
    private List<UMLAttribute> attrList = new ArrayList<UMLAttribute>();

    public UMLClass (String name) {
        super(name);
        this.isUserDefined = true;
        this.isAbstract = false;
    }

    public boolean addAttribute(UMLAttribute attr) {
        if (this.attrList.contains(attr)) {
            return false;
        } else {
            this.attrList.add(attr);
            return true;
        }
    }

    public List<UMLAttribute> getAttributes() {
        List<UMLAttribute> unmodifiableList =
                Collections.unmodifiableList(this.attrList);
        return unmodifiableList;
    }

    public int getAttrPosition(UMLAttribute attr) {
        if (this.attrList.contains(attr)) {
            return this.attrList.indexOf(attr);
        } else {
            return -1;
        }
    }

    public boolean isAbstract() {
        return this.isAbstract;
    }

    public int moveAttrAtPosition(UMLAttribute attr, int pos) {
        if (this.attrList.contains(attr)) {
            this.attrList.remove(attr);
            this.attrList.add(pos, attr);
            return 0;
        }
        else {
            return -1;
        }
    }

    public void setAbstract(boolean isAbstract) {
        this.isAbstract = isAbstract;
    }
}