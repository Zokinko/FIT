-- Meno projektu: SQL skript pre vytvorenie zakladnych objektov schemy databazy
-- Autori: Tomas Hruz <xhruzt00@stud.fit.vutbr.cz> 
--         Lukas Tkac <xtkacl00@stud.fit.vutbr.cz>

-- Vymazanie jednotlivych tabuliek nasej schemy a nasledne vymazanie vsetkych referencnych integritnych obmedzeni
DROP TABLE HracHraRelation CASCADE CONSTRAINTS;
DROP TABLE Hrac CASCADE CONSTRAINTS;
DROP TABLE Klubove_vybavenie CASCADE CONSTRAINTS;
DROP TABLE Sportovisko CASCADE CONSTRAINTS;
DROP TABLE Team CASCADE CONSTRAINTS;
DROP TABLE TeamHralRelation CASCADE CONSTRAINTS;
DROP TABLE TeamTreningRelation CASCADE CONSTRAINTS;
DROP TABLE Trener CASCADE CONSTRAINTS;
DROP TABLE Trening CASCADE CONSTRAINTS;
DROP TABLE TreningSportoviskoRelation CASCADE CONSTRAINTS;
DROP TABLE Trenuje CASCADE CONSTRAINTS;
DROP TABLE Zapas CASCADE CONSTRAINTS;

-- Vymazanie sekvencie na generovanie ID zapasov
DROP SEQUENCE zapas_seq;
-- Vymazanie sekvencie na generovanie ID hracov
DROP SEQUENCE hrac_seq;
-- Vymazanie sekvencie na generovanie ID viazanych s tabuľkou Hrac
DROP SEQUENCE hrac_rel_seq;

-- Vymazanie materializovaneho pohladu
DROP MATERIALIZED VIEW view_utocnikov;

-- Vymazanie procedúry na zistenie priemenej výšky pre tímovú kategóriu 
DROP PROCEDURE priemerna_vyska_pre_timovu_kategoriu;

-- Vymazanie procedúry na zistenie toho, čí je dostatočná kapacita štadiónu a typ
DROP PROCEDURE Kapacita_stadionu;


-- Vytvorenie zakladnych tabuliek schemy a vazobnych tabuliek
CREATE TABLE Hrac(
id_hrac INTEGER NOT NULL, -- primarny kluc 
meno VARCHAR(50) NOT NULL,
adresa_bydliska VARCHAR(100),
datum_narodenia DATE NOT NULL,
vyska INTEGER CHECK (vyska>=0) NOT NULL, 
vaha INTEGER CHECK (vaha>=0) NOT NULL  
);

CREATE TABLE Klubove_vybavenie(
typ VARCHAR(50) NOT NULL, -- primarny kluc 
cena INTEGER CHECK (cena>=0)
);

CREATE TABLE Team(
id_tim INTEGER NOT NULL, -- primarny kluc 
kategoria VARCHAR(50) NOT NULL
);

CREATE TABLE Trener(
id_trener INTEGER NOT NULL, -- primarny kluc 
meno VARCHAR(50) NOT NULL,
adresa_bydliska VARCHAR(100) NOT NULL,
datum_narodenia DATE NOT NULL
);

CREATE TABLE Trening(
id_treningu INTEGER NOT NULL, -- primarny kluc 
datum_a_cas_treningu TIMESTAMP NOT NULL,
id_trener INTEGER NOT NULL
);

CREATE TABLE Zapas(
id_zapasu INTEGER NOT NULL, -- primarny kluc 
datum_a_cas_konania TIMESTAMP NOT NULL,
adresa VARCHAR(100) NOT NULL,
kolo_ligy INTEGER CHECK (kolo_ligy>=0),
vysledok_zapasu VARCHAR(10),
-- IMPORTANT: Pridany atribut oproti rieseniu v casti 1. Oprava na zaklade komentara ku hodnoteniu prvej casti projektu.
superiaci_tim VARCHAR(50) NOT NULL 
);

CREATE TABLE Sportovisko(
id_sportovisko INTEGER NOT NULL, -- primarny kluc 
nazov_sportoviska VARCHAR(50) NOT NULL,
adresa VARCHAR(100) NOT NULL,
typ VARCHAR(50),
kapacita_divakov INTEGER CHECK (kapacita_divakov>=0),
kapacita_hracov INTEGER CHECK (kapacita_hracov>=0),
vlastnictvo VARCHAR(50) NOT NULL
);

-- Vazobna tabulka Hrac->Team; Team->Hrac
CREATE TABLE HracHraRelation(
id_hrac_rel INTEGER NOT NULL,
id_tim_rel INTEGER NOT NULL,
post VARCHAR(20) NOT NULL,
cislo_dresu INTEGER NOT NULL
);

-- Vazobna tabulka Team->Trener; Trener->Team
CREATE TABLE Trenuje (
id_team_rel INTEGER NOT NULL,
id_trener_rel INTEGER NOT NULL,
funkcia_v_time VARCHAR(50)
);

-- Vazobna tabulka Trening->Sportovisko; Sportovisko->Trening
CREATE TABLE TreningSportoviskoRelation(
id_trening_rel INTEGER NOT NULL,
id_sportovisko_rel INTEGER NOT NULL
);

-- Vazobna tabulka Team->Trening; Trening->Team
CREATE TABLE TeamTreningRelation (
id_team_sa_zucastnuje INTEGER NOT NULL,
id_treningu_sa_zucastnuje INTEGER NOT NULL
);

-- -- Vazobna tabulka TeamHralRelation->Zapas; Zapas->TeamHralRelation
CREATE TABLE TeamHralRelation (
id_team_hral_zapas INTEGER NOT NULL,
id_zapas_hral_team INTEGER NOT NULL
);

-- PRIMARNE KLUCE 
ALTER TABLE Hrac
ADD CONSTRAINT PK_Hrac PRIMARY KEY (id_hrac);

ALTER TABLE Klubove_vybavenie
ADD CONSTRAINT PK_Klubove_vybavenie PRIMARY KEY (typ);

ALTER TABLE Team
ADD CONSTRAINT PK_tim PRIMARY KEY (id_tim);

ALTER TABLE Trener
ADD CONSTRAINT PK_Trener PRIMARY KEY (id_trener);

ALTER TABLE Trenuje
ADD CONSTRAINT PK_Trenuje PRIMARY KEY (id_team_rel, id_trener_rel);

ALTER TABLE Trening
ADD CONSTRAINT PK_Trening PRIMARY KEY (id_treningu);

ALTER TABLE Zapas
ADD CONSTRAINT PK_Zapas PRIMARY KEY (id_zapasu);

ALTER TABLE Sportovisko
ADD CONSTRAINT PK_Sportovisko PRIMARY KEY (id_sportovisko);

ALTER TABLE TreningSportoviskoRelation
ADD CONSTRAINT PK_TreningSportoviskoRelation PRIMARY KEY (id_trening_rel, id_sportovisko_rel);

ALTER TABLE HracHraRelation
ADD CONSTRAINT PK_HracHraRelation PRIMARY KEY (id_hrac_rel, id_tim_rel);

ALTER TABLE TeamTreningRelation
ADD CONSTRAINT PK_TeamTreningRelation PRIMARY KEY (id_team_sa_zucastnuje, id_treningu_sa_zucastnuje);

ALTER TABLE TeamHralRelation
ADD CONSTRAINT PK_TeamHralRelation PRIMARY KEY (id_team_hral_zapas, id_zapas_hral_team);


-- CUDZIE KLUCE 
ALTER TABLE Trening 
ADD CONSTRAINT FK_id_trener FOREIGN KEY (id_trener) REFERENCES Trener ON DELETE CASCADE;

-- cudzie kluce pre vazobnu tabulku medzi Team a Trener
ALTER TABLE Trenuje 
ADD CONSTRAINT FK_id_team_rel FOREIGN KEY (id_team_rel) REFERENCES Team ON DELETE CASCADE;

ALTER TABLE Trenuje 
ADD CONSTRAINT FK_id_trener_rel FOREIGN KEY (id_trener_rel) REFERENCES Trener ON DELETE CASCADE;

-- cudzie kluce pre vazobnu tabulku medzi Trening a Sportovisko
ALTER TABLE TreningSportoviskoRelation 
ADD CONSTRAINT FK_id_trening FOREIGN KEY (id_trening_rel) REFERENCES Trening ON DELETE CASCADE;

ALTER TABLE TreningSportoviskoRelation
ADD CONSTRAINT FK_id_sportovisko FOREIGN KEY (id_sportovisko_rel) REFERENCES Sportovisko ON DELETE CASCADE;

-- cudzie kluce pre vazobnu tabulku medzi Hrac a Team
ALTER TABLE HracHraRelation 
ADD CONSTRAINT FK_id_hrac_rel FOREIGN KEY (id_hrac_rel) REFERENCES Hrac ON DELETE CASCADE;

ALTER TABLE HracHraRelation
ADD CONSTRAINT FK_id_tim_rel FOREIGN KEY (id_tim_rel) REFERENCES Team ON DELETE CASCADE;

-- cudzie kluce pre vazobnu tabulku medzi Team a Trening
ALTER TABLE TeamTreningRelation 
ADD CONSTRAINT FK_id_team_sa_zucastnuje FOREIGN KEY (id_team_sa_zucastnuje) REFERENCES Team ON DELETE CASCADE;

ALTER TABLE TeamTreningRelation
ADD CONSTRAINT FK_id_trening_sa_zucastnuje FOREIGN KEY (id_treningu_sa_zucastnuje) REFERENCES Trening ON DELETE CASCADE;

-- cudzie kluce pre vazobnu tabulku medzi Team a Zapas
ALTER TABLE TeamHralRelation 
ADD CONSTRAINT FK_id_team_hral_zapas FOREIGN KEY (id_team_hral_zapas) REFERENCES Team ON DELETE CASCADE;

ALTER TABLE TeamHralRelation
ADD CONSTRAINT FK_id_zapas_hral_team FOREIGN KEY (id_zapas_hral_team) REFERENCES Zapas ON DELETE CASCADE;

-- TRIGGERY
--1. Trigger pre automaticky generované primárne kľúče zápasu
CREATE SEQUENCE zapas_seq
INCREMENT BY 1
START WITH 1;

CREATE OR REPLACE TRIGGER zapas_id_trg
    BEFORE INSERT
    ON Zapas
    FOR EACH ROW 
BEGIN
:NEW.id_zapasu := zapas_seq.nextval;
END;
/

-- 2. Trigger kontrolujúci správnosť pri vkladaní zápasov
CREATE OR REPLACE TRIGGER zapas_trg
    BEFORE INSERT OR UPDATE
    ON Zapas
    FOR EACH ROW 
BEGIN
    IF (:NEW.vysledok_zapasu IS NOT NULL) THEN
        IF (:NEW.datum_a_cas_konania > CURRENT_TIMESTAMP) THEN
            RAISE_APPLICATION_ERROR(-20001, 'Zápas sa ešte neodohral');
        END IF;
    END IF;
END;
/

-- 3. Trigger pre automaticky generované kľúče u hráčov
CREATE SEQUENCE hrac_seq
INCREMENT BY 1
START WITH 1;

CREATE OR REPLACE TRIGGER hrac_id_trg
    BEFORE INSERT
    ON Hrac
    FOR EACH ROW 
BEGIN
:NEW.id_hrac := hrac_seq.nextval;
END;
/

-- 4. Trigger pre automaticky generované kľúče väzobnej tabuľky viazanej identifikátormi na tabuľku Hrac. (v tomto prípade) 
-- Upresnenie: Relačné identifikátory viazané na tabuľku Team negenerujeme iteratívne s krokom k=1. Hráči sú totiž explicitne priraďovaní do kategorií tímov.
CREATE SEQUENCE hrac_rel_seq
INCREMENT BY 1
START WITH 1;

CREATE OR REPLACE TRIGGER hrac_rel_id_trg
    BEFORE INSERT
    ON HracHraRelation
    FOR EACH ROW 
BEGIN
:NEW.id_hrac_rel := hrac_rel_seq.nextval;
END;
/


-- 5. Trigger pre stráženie spodnej vekovej hranice hráčov.
--    V klube hrajú hráči starší ako 6 rokov vrátane (+/- rok tolerancia kvôli nádejným talentom mladším trocha ako 6 rokov).
CREATE OR REPLACE TRIGGER hrac_datum_trg
    BEFORE INSERT OR UPDATE
    OF datum_narodenia ON Hrac
    FOR EACH ROW 
BEGIN
    IF (EXTRACT(YEAR FROM CURRENT_DATE()) - EXTRACT(YEAR FROM :NEW.datum_narodenia) < 6) THEN
        RAISE_APPLICATION_ERROR(-20000, 'Hráč je príliš mladý');
    END IF;
END;
/

SET SERVEROUTPUT ON;
----- PROCEDURY -----
--1. Sportoviska ktore budu splnovat kapacitu pre zapasy s urcitou minimalnou velkostou
--   a typom sportoviska

CREATE OR REPLACE PROCEDURE Kapacita_stadionu (kapacita INTEGER, typ_stadionu VARCHAR)
AS
    CURSOR sportoviska IS 
    SELECT * FROM Sportovisko;
    sportoviskoRow sportoviska%ROWTYPE;
BEGIN
    dbms_output.put_line('Sportoviska s pozadovanou kapacitou divakov: ' || kapacita || ' , a typom: ' || typ_stadionu); 
    OPEN sportoviska;
    LOOP 
        FETCH sportoviska INTO sportoviskoRow; 
        EXIT WHEN sportoviska%notfound; 
        IF sportoviskoRow.kapacita_divakov > kapacita THEN
            IF typ_stadionu = sportoviskoRow.typ THEN
                dbms_output.put_line('Nazov: ' || sportoviskoRow.nazov_sportoviska  || ' Adresa: ' ||  sportoviskoRow.adresa);
            END IF;
        END IF;
     END LOOP; 
    CLOSE sportoviska; 

EXCEPTION WHEN OTHERS THEN
    RAISE_APPLICATION_ERROR(-20001, 'Chyba pri vykonavani procedury Kapacita_stadionu()');
END;
/

-- 2. Procedúra pre zistenie priemernej výšky hráčov pre jednotlivú tímovú kategóriu

CREATE OR REPLACE PROCEDURE priemerna_vyska_pre_timovu_kategoriu (nazov_kategorie IN VARCHAR) AS
BEGIN
    DECLARE
    -- pre ukážku je použitá programátorom definovaná výnimka namiesto preddefinovanej
    -- (v tomto prípade sa dá použiť preddefinovaná výnimka ZERO_DIVIDE)
    -- Predpokladáme, že nechceme používať preddefinovavé chybové výstupy pri každej procedúre.
    exception_ziadny_hraci EXCEPTION;
    -- deklarácia premenných pre výpočet priemeru výšky hráčov
    suma_vysiek_hracov NUMBER;
    pocet_hracov NUMBER;
    priemerna_vyska NUMBER;
    
    -- Definícia kurzora. 
    -- A to pre získavanie záznamov o výške jednotlivých hráčov v požadovanej tímovej kategórií
    -- ktorá je zadaná uživateľom na VSTUPE procedúry 
    CURSOR cursor_vyska_hracov IS
        SELECT Hrac.vyska 
        FROM Hrac JOIN HracHraRelation ON Hrac.id_hrac = HracHraRelation.id_hrac_rel
              JOIN Team ON id_tim_rel = id_tim
        WHERE Team.kategoria = nazov_kategorie;       
        zaznam_vyska_hraca  cursor_vyska_hracov%ROWTYPE; 
    BEGIN
    IF NOT cursor_vyska_hracov%ISOPEN THEN
        OPEN cursor_vyska_hracov;
    END IF;
    suma_vysiek_hracov := 0;
    pocet_hracov := 0;
    priemerna_vyska := 0;
    -- spracujeme každý jeden záznam odpovedajúci požadovanej kategórií
    LOOP
        FETCH cursor_vyska_hracov INTO zaznam_vyska_hraca;
        EXIT WHEN cursor_vyska_hracov%NOTFOUND;
        pocet_hracov := pocet_hracov + 1;
        suma_vysiek_hracov := suma_vysiek_hracov + zaznam_vyska_hraca.vyska;
    END LOOP;   
    CLOSE cursor_vyska_hracov;
    -- Kontrola či v danej kategórii hráčov sú hráči, ak nie vyvoláme výnimku
    IF pocet_hracov=0 THEN
        RAISE exception_ziadny_hraci;
    END IF;
    -- Výpočet priemenej výšky hráčov pre požadovanú kategóriu.
    priemerna_vyska := suma_vysiek_hracov / pocet_hracov;
    DBMS_OUTPUT.put_line('Pocet hracov: ' || pocet_hracov);
    DBMS_OUTPUT.put_line('Priemerna vyska pre kategoriu ' || nazov_kategorie || ' : ' || priemerna_vyska || ' ' || 'cm'); 
    
    EXCEPTION
        WHEN exception_ziadny_hraci THEN 
            DBMS_OUTPUT.put_line('');
            DBMS_OUTPUT.put_line('Pocet hracov: ' || pocet_hracov);
            DBMS_OUTPUT.put_line('Priemerna vyska pre kategoriu ' || nazov_kategorie || ' : ' || priemerna_vyska || ' ' || 'cm'); 
            RAISE_APPLICATION_ERROR(-20002, 'V uvedenej kategorií nie sú žiadny hráči');
        WHEN OTHERS THEN
            -- navrátenie zmien, ktoré boli vykonané počas tejto transakcie
            ROLLBACK;      
    END;
END;
/

-- VKLADANIE DAT
-- vkladane data pre Hrac
INSERT INTO Hrac (meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Tony Stark', 'Bozetechova 45', TO_DATE('15.12.1998', 'dd.mm.yyyy'), 180, 65);

INSERT INTO Hrac (meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Peter Parker', 'Bozetechova 46', TO_DATE('5.11.1997', 'dd.mm.yyyy'), 182, 65);

INSERT INTO Hrac (meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Bruce Wayne', 'Bozetechova 47', TO_DATE('25.7.1995', 'dd.mm.yyyy'), 199, 65);

INSERT INTO Hrac (meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Bruce Banner', 'Bozetechova 415', TO_DATE('30.6.1988', 'dd.mm.yyyy'), 166, 73);

INSERT INTO Hrac (meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Steve Rogers', 'Bozetechova 445', TO_DATE('16.3.1998', 'dd.mm.yyyy'), 183, 65);

INSERT INTO Hrac (meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Bucky Barns', 'Bozetechova 4455', TO_DATE('15.8.1998', 'dd.mm.yyyy'), 175, 66);

INSERT INTO Hrac (meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Thor', 'Bozetechova 245', TO_DATE('11.3.1998', 'dd.mm.yyyy'), 180, 65);

INSERT INTO Hrac (meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Lex Luthor', 'Bozetechova 12', TO_DATE('8.12.1998', 'dd.mm.yyyy'), 180, 80);

INSERT INTO Hrac (meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Frodo', 'Bozetechova 225', TO_DATE('1.3.1990', 'dd.mm.yyyy'), 180, 65);

INSERT INTO Hrac ( meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Aragorn', 'Bozetechova 77', TO_DATE('2.10.1997', 'dd.mm.yyyy'), 176, 65);

INSERT INTO Hrac ( meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Boromir', 'Bozetechova 48', TO_DATE('15.3.1996', 'dd.mm.yyyy'), 180, 65);

INSERT INTO Hrac ( meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Faramir', 'Bozetechova 42', TO_DATE('15.6.1998', 'dd.mm.yyyy'), 154, 70);

INSERT INTO Hrac ( meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Gandalf', 'Bozetechova 35', TO_DATE('25.3.1995', 'dd.mm.yyyy'), 180, 65);

INSERT INTO Hrac ( meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Pipin', 'Bozetechova 488', TO_DATE('5.4.1998', 'dd.mm.yyyy'), 183, 65);

INSERT INTO Hrac ( meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Saruman', 'Bozetechova 999', TO_DATE('30.3.1994', 'dd.mm.yyyy'), 167, 65);

INSERT INTO Hrac ( meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Evzen', 'Bozetechova 42', TO_DATE('30.3.2000', 'dd.mm.yyyy'), 177, 75);

-- vkladane data pre Klubove vybavenie
INSERT INTO Klubove_vybavenie (typ, cena) VALUES ('Lopta Najky', 250);
INSERT INTO Klubove_vybavenie (typ, cena) VALUES ('Bránka čierna', 2500);
INSERT INTO Klubove_vybavenie (typ, cena) VALUES ('Bránka biela', 2500);
INSERT INTO Klubove_vybavenie (typ, cena) VALUES ('Lopta adeedas', 250);
INSERT INTO Klubove_vybavenie (typ, cena) VALUES ('Píšťaľka', 100);
INSERT INTO Klubove_vybavenie (typ)       VALUES ('Lopta pooma');

-- vkladane data pre Tim
INSERT INTO Team (id_tim, kategoria) VALUES (1, 'Dorast');
INSERT INTO Team (id_tim, kategoria) VALUES (2, 'Dospeli');
INSERT INTO Team (id_tim, kategoria) VALUES (3, 'Deti');

-- vkladane data pre Trener
INSERT INTO Trener (id_trener, meno, adresa_bydliska, datum_narodenia)
VALUES (1, 'Sauron', 'Rufusova 49', TO_DATE('14.2.1966', 'dd.mm.yyyy'));

INSERT INTO Trener (id_trener, meno, adresa_bydliska, datum_narodenia) 
VALUES (2, 'Voldemort', 'Sauronova 11', TO_DATE('11.7.1955', 'dd.mm.yyyy'));

-- vkladane data pre Trening
INSERT INTO Trening (id_treningu, datum_a_cas_treningu, id_trener) 
VALUES (15, TO_TIMESTAMP('10-09-2021 14:10:00', 'DD-MM-YYYY HH24:MI:SS'), 1);

INSERT INTO Trening (id_treningu, datum_a_cas_treningu, id_trener) 
VALUES (16, TO_TIMESTAMP('17-09-2021 13:15:00', 'DD-MM-YYYY HH24:MI:SS'), 2);

-- vkladane data pre Zapas
INSERT INTO Zapas (datum_a_cas_konania, adresa, kolo_ligy, vysledok_zapasu, superiaci_tim) 
VALUES (TO_TIMESTAMP('15-11-2020 17:00:00', 'DD-MM-YYYY HH24:MI:SS'), 'Cervinkova 66', 3, '3:0', 'FC Barcelona');

INSERT INTO Zapas (datum_a_cas_konania, adresa, kolo_ligy, vysledok_zapasu, superiaci_tim) 
VALUES (TO_TIMESTAMP('22-11-2020 16:30:00', 'DD-MM-YYYY HH24:MI:SS'), 'Cervinkova 66', 3, '4:3', 'FC Sarajevo');

INSERT INTO Zapas (datum_a_cas_konania, adresa, kolo_ligy, vysledok_zapasu, superiaci_tim) 
VALUES (TO_TIMESTAMP('10-12-2020 17:00:00', 'DD-MM-YYYY HH24:MI:SS'), 'Cervinkova 66', 4, '0:2', 'FC Brno');

-- vkladane data pre Sportovisko
INSERT INTO Sportovisko (id_sportovisko, nazov_sportoviska, adresa, typ, kapacita_divakov, kapacita_hracov, vlastnictvo) 
VALUES (1, 'SuperStadium', 'Cervinkova 66', 'otvoreny',5000, 100, 'VUT FIT');

INSERT INTO Sportovisko (id_sportovisko, nazov_sportoviska, adresa, typ, kapacita_divakov, kapacita_hracov, vlastnictvo) 
VALUES (2, 'LessSuperStadium', 'Cervinkova 68', 'otvoreny',4000, 50, 'MUNI FI');

-- vkladane data pre HracHraRelation
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (1, 'brankar', 1);
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (1, 'obrana', 2);
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (1, 'obrana', 3);
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (1, 'zaloha', 4);
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (1, 'utok', 5);

INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (2, 'brankar', 3);
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (2, 'obrana', 2);
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (2, 'obrana', 6);
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (2, 'zaloha', 7);
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (2, 'utok', 11);

INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (1, 'brankar', 99);
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (1, 'obrana', 10);
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (1, 'obrana', 7);
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (1, 'zaloha', 23);
INSERT INTO HracHraRelation (id_tim_rel, post, cislo_dresu) VALUES (1, 'utok', 11);

-- vkladane data pre Trenuje 
INSERT INTO Trenuje (id_team_rel, id_trener_rel, funkcia_v_time) VALUES (1, 1, 'hlavny trener');
INSERT INTO Trenuje (id_team_rel, id_trener_rel, funkcia_v_time) VALUES (2, 1, 'asistent trenera');
INSERT INTO Trenuje (id_team_rel, id_trener_rel, funkcia_v_time) VALUES (3, 1, 'trener brankarov');

INSERT INTO Trenuje (id_team_rel, id_trener_rel, funkcia_v_time) VALUES (1, 2, 'asistent trenera');
INSERT INTO Trenuje (id_team_rel, id_trener_rel, funkcia_v_time) VALUES (2, 2, 'kondicny trener');
INSERT INTO Trenuje (id_team_rel, id_trener_rel, funkcia_v_time) VALUES (3, 2, 'hlavny trener');

-- vkladane data pre TreningSportoviskoRelation
INSERT INTO TreningSportoviskoRelation (id_trening_rel, id_sportovisko_rel) VALUES (15,1);
INSERT INTO TreningSportoviskoRelation (id_trening_rel, id_sportovisko_rel) VALUES (15,2);
INSERT INTO TreningSportoviskoRelation (id_trening_rel, id_sportovisko_rel) VALUES (16,1);
INSERT INTO TreningSportoviskoRelation (id_trening_rel, id_sportovisko_rel) VALUES (16,2);

-- vkladane data pre TeamTreningRelation
INSERT INTO TeamTreningRelation (id_team_sa_zucastnuje, id_treningu_sa_zucastnuje) VALUES (1, 15);
INSERT INTO TeamTreningRelation (id_team_sa_zucastnuje, id_treningu_sa_zucastnuje) VALUES (2, 15);
INSERT INTO TeamTreningRelation (id_team_sa_zucastnuje, id_treningu_sa_zucastnuje) VALUES (3, 16);

-- vkladane data pre TeamHralRelation
INSERT INTO TeamHralRelation (id_team_hral_zapas, id_zapas_hral_team) VALUES (1, 1);
INSERT INTO TeamHralRelation (id_team_hral_zapas, id_zapas_hral_team) VALUES (2, 3);


-- Projekt časť 3.

-- Aspoň? 2x požiadavka SELECT pre spojejenie informácií z dvoch tabuliek.
-- 1. Ktorý hráči hrajú na poste obrancu ? 
SELECT Hrac.meno, HracHraRelation.post
FROM Hrac JOIN HracHraRelation ON Hrac.id_hrac = HracHraRelation.id_hrac_rel 
WHERE HracHraRelation.post='obrana';

-- 2. Aké zápasy sa odohrali na štadióne SuperStadium?
SELECT Zapas.datum_a_cas_konania, Zapas.adresa, Zapas.kolo_ligy, Zapas.vysledok_zapasu, Zapas.superiaci_tim, Sportovisko.nazov_sportoviska
FROM Zapas JOIN Sportovisko ON Zapas.adresa = Sportovisko.adresa
WHERE Sportovisko.adresa='Cervinkova 66';

-- Požiadavka SELECT pre spojenie informácií z troch tabuliek
-- 1. Ktorý tréner/tréneri trénujú dorasteneckú kategóriu a aké trenérske funkcie v tíme zastávjú?
SELECT Trener.meno, Trenuje.funkcia_v_time, Team.kategoria
FROM Trener JOIN Trenuje ON Trener.id_trener = Trenuje.id_trener_rel
            JOIN Team ON id_team_rel = id_tim
WHERE Team.kategoria='Dorast';

-- Dve požiadavky s klauzulou GROUP BY a agregačnou funkciou
-- 1. Koľko hráčov hrá v jednotlivých kategóriach tímov ? 
SELECT Team.kategoria, COUNT(*) AS POCET_HRACOV
FROM Hrac JOIN HracHraRelation ON Hrac.id_hrac = HracHraRelation.id_hrac_rel
          JOIN Team ON id_tim_rel = id_tim
GROUP BY Team.kategoria;

-- 2. Koľko zápasov bolo odhratých v jednotlivých kategóriach tímov ? 
SELECT Team.kategoria, COUNT(*) as POCET_ZAPASOV_V_KATEGORII
FROM Team JOIN TeamHralRelation ON Team.id_tim = TeamHralRelation.id_team_hral_zapas
          JOIN Zapas ON TeamHralRelation.id_zapas_hral_team = Zapas.id_zapasu
GROUP BY Team.kategoria;

-- Jedna požiadavka obsahujúca predikát EXISTS 
--  1.Existuje nejaký hráč s číslom 99?
SELECT Hrac.meno
FROM Hrac
WHERE EXISTS (SELECT HracHraRelation.id_hrac_rel 
              FROM HracHraRelation 
              WHERE Hrac.id_hrac = HracHraRelation.id_hrac_rel AND cislo_dresu = 99);

-- Jedna požiadavka s predikátom IN s vnoreným SELECTom (nie IN s množinou konštantných dát)
-- 1. Ktorý hráči boli narodený medzi rokmi 1998 a 2000?
SELECT Hrac.meno, Hrac.datum_narodenia
FROM Hrac
WHERE Hrac.datum_narodenia IN 
(SELECT datum_narodenia FROM Hrac 
WHERE datum_narodenia BETWEEN '01-JAN-1998' AND '31-DEC-2000');


-- Projekt časť 4/5.

--- PRÍKLADY TRIGGEROV ---
-- Minimálne 2 triggery.

-- 1. Generovanie ID zápasu, ID sa nevkladaju manualne ale su generovane automaticky
INSERT INTO Zapas (datum_a_cas_konania, adresa, kolo_ligy, vysledok_zapasu, superiaci_tim) 
VALUES (TO_TIMESTAMP('10-12-2020 17:00:00', 'DD-MM-YYYY HH24:MI:SS'), 'Cervinkova 66', 4, '0:2', 'FC Brno');
SELECT * FROM Zapas;

-- 2. Zápas nemôže mať výsledok pokiaľ sa ešte neodohral
--Prvý zápas vloží správne, pretože ak nemá zadaný výsledok tak dátum môže byť v budúcnosti
--Druhý zápas má zadaný výsledok to ale znamená, že sa už musel uskutočniť, tým pádom hodí chybu
INSERT INTO Zapas (datum_a_cas_konania, adresa, kolo_ligy, superiaci_tim) 
VALUES (TO_TIMESTAMP('19-8-2021 17:00:00', 'DD-MM-YYYY HH24:MI:SS'), 'Cervinkova 66', 4, 'FC Brno');

INSERT INTO Zapas (datum_a_cas_konania, adresa, kolo_ligy, vysledok_zapasu, superiaci_tim) 
VALUES (TO_TIMESTAMP('19-8-2021 17:00:00', 'DD-MM-YYYY HH24:MI:SS'), 'Cervinkova 66', 4, '0:2', 'FC Brno');

-- 3. a 4. Trigery 3.hrac_id_trg a 4.hrac_rel_id_trg po vyvolaní akciou pred akciou INSERT rovnako generujú identifikátory
-- ako trigger zapas_id_trg.

-- 5. Trigger pre stráženie spodnej vekovej hranice hráčov.
--    V klube hrajú hráči starší ako 6 rokov vrátane (+/- rok tolerancia kvôli nádejným talentom mladším trocha ako 6 rokov).

-- Ukážka, toho ak je hráč mladší ako 6 rokov
INSERT INTO Hrac ( meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES ('Frydrych Chrobak', 'Masarykova 13 ', TO_DATE('01.01.2016', 'dd.mm.yyyy'), 154, 40);


--- UKÁŽKY PROCEDÚR --- 

-- 1. Procedura, ktora nam vrati, na ktorych sportoviskach mozme hrat zapas,
--    tak aby sa tam zmestilo aspon 4000 divakov a bol to otvoreny stadion
BEGIN
    Kapacita_stadionu (4000, 'otvoreny');
END;
/
INSERT INTO Sportovisko (id_sportovisko, nazov_sportoviska, adresa, typ, kapacita_divakov, kapacita_hracov, vlastnictvo) 
VALUES (3, 'BigEnoughStadium', 'Cervinkova 11', 'kryty',4001, 100, 'VUT FIT');

INSERT INTO Sportovisko (id_sportovisko, nazov_sportoviska, adresa, typ, kapacita_divakov, kapacita_hracov, vlastnictvo) 
VALUES (4, 'NotBigEnoughStadium', 'Cervinkova 32', 'otvoreny',3999, 100, 'VUT FIT');

INSERT INTO Sportovisko (id_sportovisko, nazov_sportoviska, adresa, typ, kapacita_divakov, kapacita_hracov, vlastnictvo) 
VALUES (5, 'BigEnoughStadium', 'Bozetechova 1', 'otvoreny',10000, 150, 'VUT FIT');
BEGIN
    Kapacita_stadionu (4000, 'otvoreny');
END;
/

-- 2. Procedúra pre zistenie priemernej výšky hráčov pre jednotlivú tímovú kategóriu. 
--    Ak nie sú žiadny hráči v tímovej kategórií, ktorú užívateľ zadá na VSTUP,
-- tak je vypísaný nulový výstup a vyvolaná výnimka.

-- Ukážka: Ak nemáme požadované dáta na výpočet (V tímovej kategórií "Deti" nieje ani jeden hráč).
BEGIN
DBMS_OUTPUT.put_line(' ');
DBMS_OUTPUT.put_line('Deti');
priemerna_vyska_pre_timovu_kategoriu('Deti');
END;
/

-- Ukážka: Ak máme požadované dáta pre výpočet (tímová kategória "Dorast")
BEGIN
DBMS_OUTPUT.put_line(' ');
DBMS_OUTPUT.put_line('Dorast');
priemerna_vyska_pre_timovu_kategoriu('Dorast');
END;
/

-- Ukážka: Ak máme požadované dáta pre výpočet (tímová kategória "Dospeli")
BEGIN
DBMS_OUTPUT.put_line(' ');
DBMS_OUTPUT.put_line('Dospeli');
priemerna_vyska_pre_timovu_kategoriu('Dospeli');
END;
/

-- DROP INDEX idx_hra;
-- DROP INDEX idx_tiiim;

-- Prvý výpis pre uskutočnenie databázového dotazu so spojením aspoň dvoch tabuliek,
-- agregačnou funkciou a klauzulou GROUP BY.
-- 1. Priemerná váha hráčov pre jednotlivé tímové kategórie. (Ak sa v timovej kategorií nachádza aspoň jeden hráč)
EXPLAIN PLAN FOR
SELECT Team.kategoria, AVG(Hrac.vaha) AS PRIEMERNA_VAHA_TIMOVEJ_KATEGORIE
FROM Hrac JOIN HracHraRelation ON Hrac.id_hrac = HracHraRelation.id_hrac_rel
          JOIN Team ON id_tim_rel = id_tim
GROUP BY Team.kategoria;

-- Zobraz plán ešte BEZ explicitne vytvoreného indexu alebo aplikovanej nápovedy pre optimalizátor.
SELECT PLAN_TABLE_OUTPUT FROM table (DBMS_XPLAN.DISPLAY()); 

-- Explicitné vytvorenie indexu pre ooptimalizáciu spracovanie obrazov
-- + prísluchajúca požiadavka, na ktorú má index vliv 

-- Pozostatok snahy optimalizovať pomocou explicitne vytvorenych indexov,
-- rozhodli sme sa, ze poradime optimalizatoru pomocou nápovedy (viac popísané v dokumentácií).

--CREATE INDEX idx_hra ON Hrac(ID_HRAC, VAHA);
--CREATE INDEX idx_tiiim ON Team(ID_TIM, KATEGORIA); 

-- Druhý výpis
EXPLAIN PLAN FOR
SELECT  /*+ USE_HASH(Team Hrac HracHraRelation) */ Team.kategoria, AVG(Hrac.vaha) AS PRIEMERNA_VAHA_TIMOVEJ_KATEGORIE
FROM Hrac JOIN HracHraRelation ON Hrac.id_hrac = HracHraRelation.id_hrac_rel
          JOIN Team ON id_tim_rel = id_tim
GROUP BY Team.kategoria;

-- Zobraz plán S explicitne vytvoreným indexom alebo aplikovanej nápovedy pre optimalizátor.
SELECT PLAN_TABLE_OUTPUT FROM table (DBMS_XPLAN.DISPLAY());


--- DEFINÍCIA PRÍSTUPOVÝCH PRÁV
-- Pristup pre druheho clena timu. Spúšťaný užívateľom xhruzt00
GRANT SELECT ON Sportovisko TO xtkacl00;
GRANT SELECT ON Zapas TO xtkacl00;
GRANT SELECT ON Trener TO xtkacl00;
GRANT ALL ON HracHraRelation TO xtkacl00;
GRANT ALL ON Hrac TO xtkacl00;
GRANT ALL ON Klubove_vybavenie TO xtkacl00;
GRANT ALL ON Team TO xtkacl00;
GRANT ALL ON TeamHralRelation TO xtkacl00;
GRANT ALL ON TeamTreningRelation TO xtkacl00;
GRANT ALL ON Trening TO xtkacl00;
GRANT ALL ON TreningSportoviskoRelation TO xtkacl00;
GRANT ALL ON Trenuje TO xtkacl00;
GRANT ALL ON HracHraRelation TO xtkacl00;
GRANT ALL ON Kapacita_stadionu TO xtkacl00;

--- MATERIALIZOVANÝ POHLAD ---
-- Vytvorenie materializovaneho pohladu. Spúšťaný užívateľom xtkacl00.
CREATE MATERIALIZED VIEW view_utocnikov
BUILD IMMEDIATE
REFRESH
ON COMMIT
AS
SELECT xhruzt00.Hrac.meno, xhruzt00.HracHraRelation.post
FROM xhruzt00.Hrac JOIN xhruzt00.HracHraRelation ON xhruzt00.Hrac.id_hrac = xhruzt00.HracHraRelation.id_hrac_rel 
WHERE xhruzt00.HracHraRelation.post='utok';

-- Vkladanie noveho utocnika. Spúšťaný užívateľom xtkacl00.
SELECT * FROM view_utocnikov;
INSERT INTO  xhruzt00.Hrac (id_hrac, meno, adresa_bydliska, datum_narodenia, vyska, vaha) 
VALUES (25, 'Cristiano Ronaldo', 'Skacelova 23', TO_DATE('15.2.1995', 'dd.mm.yyyy'), 190, 75);
INSERT INTO  xhruzt00.HracHraRelation (id_hrac_rel, id_tim_rel, post, cislo_dresu) VALUES (25, 1, 'utok', 83);
COMMIT;
SELECT * FROM view_utocnikov;
