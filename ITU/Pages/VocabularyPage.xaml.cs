using System;
using System.Collections.Generic;
using System.Linq;
using System.Windows;
using System.Windows.Controls;
using System.Xml.Linq;
using System.Data;
using System.Net.Http;
using System.Web.Script.Serialization;
using System.Collections;
using ITUTEST;

namespace ITUTEST.Pages
{
    public partial class VocabularyPage : Page
    {
        
        public VocabularyPage()
        {
            //nacitame dokument so slovami
            InitializeComponent();
            XDocument doc = XDocument.Load(_xmlFile);
            var result = doc;
            IEnumerable<XElement> categories = doc.Elements().Elements();

            List<string> cats = new List<string>();
            //prejdeme vsetky kategorie a tie ktore este nemame ulozime do zoznamu ktore nasledne zobrazime v listboxe na kategorie
            foreach (var category in categories)
            {
                if (!cats.Contains(category.Name.ToString()))
                {
                    cats.Add(category.Name.ToString());
                }
            }
            lbCategories.ItemsSource = cats;
        }

        string _xmlFile = @"C:\Users\tomoh\source\repos\ITUProj\PREFINAL\ITUTEST\words.xml";
        //premenna pre jazyk prekladaca
        string languageTranslator = "en";

        //funkcia vyuzivajuca google translate api na preklad slov
        //Source: https://www.codeproject.com/Tips/5247661/Google-Translate-API-Usage-in-Csharp
        public string TranslateText(string input)
        {
            // Set the language from/to in the url (or pass it into this function)
            string url = String.Format
            ("https://translate.googleapis.com/translate_a/single?client=gtx&sl={0}&tl={1}&dt=t&q={2}",
             "cs", languageTranslator, Uri.EscapeUriString(input));
            HttpClient httpClient = new HttpClient();
            string result = httpClient.GetStringAsync(url).Result;

            // Get all json data
            var jsonData = new JavaScriptSerializer().Deserialize<List<dynamic>>(result);

            // Extract just the first array element (This is the only data we are interested in)
            var translationItems = jsonData[0];

            // Translation Data
            string translation = "";

            // Loop through the collection extracting the translated objects
            foreach (object item in translationItems)
            {
                // Convert the item array to IEnumerable
                IEnumerable translationLineObject = item as IEnumerable;

                // Convert the IEnumerable translationLineObject to a IEnumerator
                IEnumerator translationLineString = translationLineObject.GetEnumerator();

                // Get first object in IEnumerator
                translationLineString.MoveNext();

                // Save its value (translated text)
                translation += string.Format(" {0}", Convert.ToString(translationLineString.Current));
            }

            // Remove first blank character
            if (translation.Length > 1) { translation = translation.Substring(1); };

            // Return translation
            return translation;
        }

        private void btnBackToMenu_Click(object sender, RoutedEventArgs e)
        {
            this.NavigationService.Navigate(new MenuPage());
        }

        private void btnCategoryEdit_Click(object sender, RoutedEventArgs e)
        {
            //ked vyberieme kategoriu na editaciu zobrazi sa v strednom gridview
            XDocument doc = XDocument.Load(_xmlFile);
            if (lbCategories.SelectedItem != null)
            {
                cbCategoryEdit.IsChecked = true;
                var result = doc.Descendants(lbCategories.SelectedItem.ToString()).Select(x => new
                {
                    Czech = x.Element("Czech").Value,
                    English = x.Element("English").Value,
                    Note = x.Element("Note").Value
                });
                dgWords.ItemsSource = result;
            }
            else { MessageBox.Show("Je potřeba vybrat kategorii pro editaci"); }

        }

        private void btnCategoryAdd_Click(object sender, RoutedEventArgs e)
        {
            XDocument doc = XDocument.Load(_xmlFile);
            //pridame slovicko do kategorie, ktora bola vybrata na upravu
            //vytvori to prazdny element ale nevadi
            if (tbCategoryAdd.Text != "" && tbCategoryAdd.Text != null)
            {
                doc.Root.Add(new XElement(tbCategoryAdd.Text,
                    new XAttribute("Name", "Slovo"),
                    new XElement("Czech", ""),
                    new XElement("English", ""),
                    new XElement("Note", "")));
                doc.Save(_xmlFile);

                //zobrazime novu kategoriu v zozname kategorii
                IEnumerable<XElement> categories = doc.Elements().Elements();

                List<string> cats = new List<string>();
                //prejdeme vsetky kategorie a tie ktore este nemame ulozime do zoznamu ktore nasledne zobrazime v listboxe na kategorie
                foreach (var category in categories)
                {
                    if (!cats.Contains(category.Name.ToString()))
                    {
                        cats.Add(category.Name.ToString());
                    }
                }
                lbCategories.ItemsSource = cats;
                //vypraznime textbox
                tbCategoryAdd.Text = "";
            }
            else { MessageBox.Show("Je potřeba zadat název nové kategorie"); }
        }

        private void btnCategoryDelete_Click(object sender, RoutedEventArgs e)
        {
            //v xml subore najdeme element ktory odpvoeda vybratemu
            XDocument doc = XDocument.Load(_xmlFile);
            if (lbCategories.SelectedItem != null)
            {
                var itemToDelete = lbCategories.SelectedItem.ToString();

                var elementsToDelete = from ele in doc.Elements("list").Elements(itemToDelete)
                                       select ele;

                //vymazeme vsetky elementy
                var elementCount = elementsToDelete.Count();
                int i = 0;
                while (i < elementCount)
                {
                    //vymazeme element so vsetkymi jeho sucastami
                    foreach (var y in elementsToDelete)
                    {
                        y.Remove();

                    }
                    i++;
                }
                doc.Save(_xmlFile);


                //znova naplnime aktualizovany zoznam kategorii
                IEnumerable<XElement> categories = doc.Elements().Elements();

                List<string> cats = new List<string>();
                //prejdeme vsetky kategorie a tie ktore este nemame ulozime do zoznamu ktore nasledne zobrazime v listboxe na kategorie
                foreach (var category in categories)
                {
                    if (!cats.Contains(category.Name.ToString()))
                    {
                        cats.Add(category.Name.ToString());
                    }
                }
                lbCategories.ItemsSource = cats;
                cbCategoryEdit.IsChecked = false;
            }
            else { MessageBox.Show("Je potřeba vybrat kategorii pro smazání"); }

        }

        //FUNKCIE PRE SLOVICKA
        private void btnSaveWord_Click(object sender, RoutedEventArgs e)
        {
            XDocument doc = XDocument.Load(_xmlFile);
            if (lbCategories.SelectedItem != null)
            {
                if (tbCzech.Text == null || tbCzech.Text == "") { MessageBox.Show("Je potřeba zadat český výraz"); return; }
                if (tbEnglish.Text == null || tbEnglish.Text == "") { MessageBox.Show("Je potřeba zadat anglický výraz"); return; }
                if (tbPoznamka.Text == null || tbPoznamka.Text == "") { tbPoznamka.Text = ""; }

                //pridame slovicko do kategorie, ktora bola vybrata na upravu
                doc.Root.Add(new XElement(lbCategories.SelectedItem.ToString(),
                    new XAttribute("Name", tbCzech.Text),
                    new XElement("Czech", tbCzech.Text),
                    new XElement("English", tbEnglish.Text),
                    new XElement("Note", tbPoznamka.Text)));
                doc.Save(_xmlFile);

                //zobrazime nove slovicka v gridview
                var result = doc.Descendants(lbCategories.SelectedItem.ToString()).Select(x => new
                {
                    Czech = x.Element("Czech").Value,
                    English = x.Element("English").Value,
                    Note = x.Element("Note").Value
                });
                dgWords.ItemsSource = result;
                //vyprazdnenie textboxov
                tbCzech.Text = "";
                tbEnglish.Text = "";
                tbPoznamka.Text = "";
            }
            else { MessageBox.Show("Je potřeba vybrat kategorii pro editaci"); }
        }

        private void btnSlovoDelete_Click(object sender, RoutedEventArgs e)
        {
            if (dgWords.SelectedItem != null)
            {
                //super vycerpavajuce ziskanie polozky na ktoru klikneme
                Object selectedWord = dgWords.SelectedItem as Object;
                var stringSelectedWord = selectedWord.ToString();
                string[] myWords = stringSelectedWord.Split('=');
                string myWords2 = myWords[1].Replace("\"", "");
                string[] myWords3 = myWords2.Split(',');
                string myWord = myWords3[0].Trim();

                //v xml subore najdeme element ktory odpvoeda vybratemu
                XDocument doc = XDocument.Load(_xmlFile);
                var elementsToDelete = from ele in doc.Element("list").Elements(lbCategories.SelectedItem.ToString())
                                       where ele != null && ele.Attribute("Name").Value.Equals(myWord)
                                       select ele;
                //vymazeme elementy 
                foreach (var y in elementsToDelete)
                {
                    y.Remove();

                }

                doc.Save(_xmlFile);
                //zobrazime nove slovicka v gridview
                var result = doc.Descendants(lbCategories.SelectedItem.ToString()).Select(x => new
                {
                    Czech = x.Element("Czech").Value,
                    English = x.Element("English").Value,
                    Note = x.Element("Note").Value
                });
                dgWords.ItemsSource = result;
            }
            else { MessageBox.Show("je potřeba vybrat slovo pro smazání"); return; }
        }

        private void btnStornoWord_Click(object sender, RoutedEventArgs e)
        {
            //vyprazdnenie textboxov
            tbCzech.Text = "";
            tbEnglish.Text = "";
            tbPoznamka.Text = "";
        }

        //prelozime slova
        private void btnTranslate_Click(object sender, RoutedEventArgs e)
        {
            if (tbCzechTranslate.Text == null || tbCzechTranslate.Text == "") { MessageBox.Show("Je potřeba zadat český výraz pro překlad"); return; }
            tbEnglishTranslate.Text = TranslateText(tbCzechTranslate.Text);            
        }

        //ukoncime editaciu kategorie
        private void btnUkoncitEdit_Click(object sender, RoutedEventArgs e)
        {
            cbCategoryEdit.IsChecked = false;
        }

        //doplnenie prelozenych slov do vkladania slov
        private void btnTranslateAutoComplete_Click(object sender, RoutedEventArgs e)
        {
            if (tbCzechTranslate.Text == null || tbCzechTranslate.Text == "") { MessageBox.Show("Je potřeba zadat český výraz pro překlad"); return; }
            if (tbEnglishTranslate.Text == null || tbEnglishTranslate.Text == "") { MessageBox.Show("Je potřeba vykonat překlad"); return; }
            //prevedieme hodnoty do textboxov na pridavanie
            tbCzech.Text = tbCzechTranslate.Text;
            tbEnglish.Text = tbEnglishTranslate.Text;
            //vynuluju sa textboxi v prekladaci
            tbCzechTranslate.Text = "";
            tbEnglishTranslate.Text = "";
        }

        //zmeny jazykov prekladaca
        private void btnUK_Click(object sender, RoutedEventArgs e)
        {
            languageTranslator = "en";
            tbLanguage.Text = "Anglický jazyk";
        }

        private void btnJA_Click(object sender, RoutedEventArgs e)
        {
            languageTranslator = "ja";
            tbLanguage.Text = "Japonský jazyk";
        }

        private void btnDE_Click(object sender, RoutedEventArgs e)
        {
            languageTranslator = "de";
            tbLanguage.Text = "Nemecký jazyk";
        }

        private void btnES_Click(object sender, RoutedEventArgs e)
        {
            languageTranslator = "es";
            tbLanguage.Text = "Španělský jazyk";
        }

        private void btnFR_Click(object sender, RoutedEventArgs e)
        {
            languageTranslator = "fr";
            tbLanguage.Text = "Francouzský jazyk";
        }
    }
}
