using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using System.Xml.Linq;

namespace ITUTEST.Pages
{
    public partial class TestPage : Page
    {
        public TestPage()
        {
            InitializeComponent();
            //nacitame kategorie do listboxu
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

        /// <summary>
        /// premenne
        /// </summary>
        string _xmlFile = @"C:\Users\tomoh\source\repos\ITUProj\PREFINAL\ITUTEST\words.xml";
        //zoznamy slov
        List<String> CzechList = new List<String>();
        List<String> EnglishList = new List<String>();
        List<String> NoteList = new List<String>();
        //iterator pre slova v testovani
        int wordIterator = 0;
        string selectedCategory;
        //pocitadla dobry a zlych slov
        int goodAnswers;
        int wrongAnswers;

        private void backToCats()
        {
            cbCategoryPick.IsChecked = false;
            //vycistime zoznamy aby sme to nemali preplnene
            EnglishList.Clear();
            CzechList.Clear();
            NoteList.Clear();
            wordIterator = 0;
            goodAnswers = 0;
            wrongAnswers = 0;
        }


        private void btnBackToMenu_Click(object sender, RoutedEventArgs e)
        {
            this.NavigationService.Navigate(new MenuPage());
        }

        private void btnBackToCategory_Click(object sender, RoutedEventArgs e)
        {
            backToCats();
        }

        //vyber kategorie na testovanie
        private void btnVybratKategorii_Click(object sender, RoutedEventArgs e)
        {
            //ked vyberieme kategoriu na editaciu zobrazi sa v strednom gridview
            XDocument doc = XDocument.Load(_xmlFile);            
            if (lbCategories.SelectedItem != null)
            {
                selectedCategory = lbCategories.SelectedItem.ToString();
                //parsujeme dokument
                var result = doc.Descendants(lbCategories.SelectedItem.ToString()).Select(x => new
                {
                    Czech = x.Element("Czech").Value,
                    English = x.Element("English").Value,
                    Note = x.Element("Note").Value
                });
                var listOfWords = result.ToList();

                //prvy skipujeme lebo je prazdny a natlacime do zoznamov
                foreach (var x in listOfWords.Skip(1))
                {
                    CzechList.Add(x.Czech.ToString());
                    EnglishList.Add(x.English.ToString());
                    NoteList.Add(x.Note.ToString());
                }

                //nastavim prve slovo do vyberu
                if (CzechList.Count == 0 ) { MessageBox.Show("Vybráná kategorie neobsahuje žádná slova."); backToCats(); return;  }
                cbCategoryPick.IsChecked = true;
                tbWordToTranslate.Text = CzechList[wordIterator];
                tbTranslatedWord.Focus();
                tbScore.Text = selectedCategory + " 0/" + CzechList.Count.ToString();
            }
            else { MessageBox.Show("Je potřeba vybrat kategorii"); }

        }


        private void btnConfirm_Click(object sender, RoutedEventArgs e)
        {
            //pocet zobrazenych otazok
            int testQuestions = 0;           
            if (CzechList.Count > 20){ testQuestions = 20; }
            else{ testQuestions = CzechList.Count; }      
            
            //pocitanie odpovedi
            if(wordIterator < testQuestions)
            {
                if (tbTranslatedWord.Text == null || tbTranslatedWord.Text == "") { MessageBox.Show("Je potřeba zadat odpověď"); return; }
                if (EnglishList[wordIterator] == tbTranslatedWord.Text)
                {
                    goodAnswers++;
                }
                else
                {
                    wrongAnswers++;
                }
                if (wordIterator < testQuestions - 1)
                {
                    //zobrazime nove slovo
                    wordIterator++;
                    tbWordToTranslate.Text = CzechList[wordIterator];
                    //vyprazdnime textbox po predchadzajucej odpovedi
                    tbTranslatedWord.Text = "";
                    tbTranslatedWord.Focus();
                    tbScore.Text = selectedCategory + " " + goodAnswers.ToString() + "/" + CzechList.Count.ToString();
                }
                else wordIterator++;
                
            }
            //presli sme vsetky otazky
            if (wordIterator == testQuestions)
            {
                tbScore.Text = "";
                tbTranslatedWord.Text = "";
                MessageBox.Show("Úspěšnost " + goodAnswers + "/" + wordIterator);

                backToCats();
            }
        }
    }
}
