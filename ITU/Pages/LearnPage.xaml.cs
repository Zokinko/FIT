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
    /// <summary>
    /// Interaction logic for LearnPage.xaml
    /// </summary>
    public partial class LearnPage : Page
    {
        public LearnPage()
        {
            InitializeComponent();
            //ked vyberieme kategoriu na editaciu zobrazi sa v strednom gridview
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
        string selectedCategory;
        //zoznamy slov
        List<String> CzechList = new List<String>();
        List<String> EnglishList = new List<String>();
        List<String> NoteList = new List<String>();
        //iterator pre slova v testovani
        int wordIterator = 0;

        private void btnBackToMenu_Click(object sender, RoutedEventArgs e)
        {
            this.NavigationService.Navigate(new MenuPage());
        }

        private void btnBackToCategory_Click(object sender, RoutedEventArgs e)
        {
            cbCategoryPick.IsChecked = false;
            //vycistime zoznamy aby sme to nemali preplnene
            EnglishList.Clear();
            CzechList.Clear();
            NoteList.Clear();
            tbScore.Text = "";
            wordIterator = 0;
            cbPreviousVisibility.IsChecked = false;
            cbNextVisibility.IsChecked = false;
        }

        private void btnVybratKategorii_Click(object sender, RoutedEventArgs e)
        {

            //ked vyberieme kategoriu na editaciu zobrazi sa v strednom gridview
            XDocument doc = XDocument.Load(_xmlFile);
            if (lbCategories.SelectedItem != null)
            {
                selectedCategory = lbCategories.SelectedItem.ToString();

                var result = doc.Descendants(lbCategories.SelectedItem.ToString()).Select(x => new
                {
                    Czech = x.Element("Czech").Value,
                    English = x.Element("English").Value,
                    Note = x.Element("Note").Value
                });
                var listOfWords = result.ToList();

                //prvy skipujeme lebo je prazdny
                foreach (var x in listOfWords.Skip(1))
                {
                    CzechList.Add(x.Czech.ToString());
                    EnglishList.Add(x.English.ToString());
                    NoteList.Add(x.Note.ToString());
                }

                if (CzechList.Count == 0) { MessageBox.Show("Vybráná kategorie neobsahuje žádná slova."); return; }
                cbCategoryPick.IsChecked = true;
                //nastavim prve slovo do vyberu
                tbCzechWord.Text = CzechList[0];
                tbEnglishWord.Text = EnglishList[0];
                tbNote.Text = NoteList[0];

                tbScore.Text = selectedCategory + " 1/" + CzechList.Count.ToString();
            }
            else { MessageBox.Show("Je potřeba vybrat kategorii"); }

            if (CzechList.Count() > 1)
            {
                cbNextVisibility.IsChecked = true;
            }
        }

        private void btnNext_Click(object sender, RoutedEventArgs e)
        {
            cbAnswerVisibility.IsChecked = false;

            //zobrazime nove slovo
            wordIterator++;

            tbCzechWord.Text = CzechList[wordIterator];
            tbEnglishWord.Text = EnglishList[wordIterator];
            tbNote.Text = NoteList[wordIterator];

            tbScore.Text = selectedCategory + " " + (wordIterator + 1).ToString() + "/" + CzechList.Count.ToString();

            cbPreviousVisibility.IsChecked = true;

            if (wordIterator == CzechList.Count() - 1)
            {
                cbNextVisibility.IsChecked = false;
                return;
            }
        }

        private void btnPrevious_Click(object sender, RoutedEventArgs e)
        {
            cbAnswerVisibility.IsChecked = false;

            wordIterator--;
            tbCzechWord.Text = CzechList[wordIterator];
            tbEnglishWord.Text = EnglishList[wordIterator];
            tbNote.Text = NoteList[wordIterator];

            tbScore.Text = selectedCategory + " " + (wordIterator + 1).ToString() + "/" + CzechList.Count.ToString();

            cbNextVisibility.IsChecked = true;
            if (wordIterator == 0)
            {
                cbPreviousVisibility.IsChecked = false;
                return;
            }


        }

        private void btnAnswer_Click(object sender, RoutedEventArgs e)
        {
            if (cbAnswerVisibility.IsChecked == true){
                cbAnswerVisibility.IsChecked = false;
            }else{
                cbAnswerVisibility.IsChecked = true;
            }
        }
    }
}
