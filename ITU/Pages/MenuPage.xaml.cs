using ITUTEST.Windows;
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

namespace ITUTEST.Pages
{
    /// <summary>
    /// Interaction logic for MenuPage.xaml
    /// </summary>
    public partial class MenuPage : Page
    {
        public MenuPage()
        {
            InitializeComponent();
        }

        private void btnMenuToVocabulary_Click(object sender, RoutedEventArgs e)
        {
            this.NavigationService.Navigate(new VocabularyPage());
        }

        private void btnMenuToTest_Click(object sender, RoutedEventArgs e)
        {
            this.NavigationService.Navigate(new TestPage());
        }

        private void btnMenuToLearn_Click(object sender, RoutedEventArgs e)
        {           
            this.NavigationService.Navigate(new LearnPage());
        }

        private void btnExit_Click(object sender, RoutedEventArgs e)
        {
            ExitWindow exitWidnow = new ExitWindow();
            exitWidnow.ShowDialog();
            // Environment.Exit(0);
        }

        private void btnSettings_Click(object sender, RoutedEventArgs e)
        {
            this.NavigationService.Navigate(new SettingsPage());
        }
    }
}
