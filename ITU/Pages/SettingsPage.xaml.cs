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
    /// Interaction logic for SettingsPage.xaml
    /// </summary>
    public partial class SettingsPage : Page
    {
        public SettingsPage()
        {
            InitializeComponent();
        }

        private void btnBackToMenu_Click(object sender, RoutedEventArgs e)
        {
            this.NavigationService.Navigate(new MenuPage());
        }

        private void btnOne_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Resources["ThemeBrush"] = Application.Current.Resources["FreshMintColor"];
            Application.Current.Resources["NavigationBarBrush"] = Application.Current.Resources["FreshPurpleColor"];
            Application.Current.Resources["TextBrush"] = Application.Current.Resources["Black"];
        }

        private void btnTwo_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Resources["ThemeBrush"] = Application.Current.Resources["FreshGreenColor"];
            Application.Current.Resources["NavigationBarBrush"] = Application.Current.Resources["DarkBlueColor"];
            Application.Current.Resources["TextBrush"] = Application.Current.Resources["Black"];
        }

        private void btnThree_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Resources["ThemeBrush"] = Application.Current.Resources["LightGreenColor"];
            Application.Current.Resources["NavigationBarBrush"] = Application.Current.Resources["SexyPinkColor"];
            Application.Current.Resources["TextBrush"] = Application.Current.Resources["Black"];
        }

        private void btnFour_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Resources["ThemeBrush"] = Application.Current.Resources["SexyPinkColor"];
            Application.Current.Resources["NavigationBarBrush"] = Application.Current.Resources["LightGreenColor"];
            Application.Current.Resources["TextBrush"] = Application.Current.Resources["Black"];
        }

        private void btnZero_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Resources["ThemeBrush"] = Application.Current.Resources["DefaultTheme"];
            Application.Current.Resources["NavigationBarBrush"] = Application.Current.Resources["DefaultNavigationBar"];
            Application.Current.Resources["TextBrush"] = Application.Current.Resources["Black"];
        }

        private void btnFive_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Resources["ThemeBrush"] = Application.Current.Resources["SandyBeigeColor"];
            Application.Current.Resources["NavigationBarBrush"] = Application.Current.Resources["SandyBrownColor"];
            Application.Current.Resources["TextBrush"] = Application.Current.Resources["Black"];
        }
        private void btnSix_Click(object sender, RoutedEventArgs e)
        {
            Application.Current.Resources["ThemeBrush"] = Application.Current.Resources["LightGray"];
            Application.Current.Resources["NavigationBarBrush"] = Application.Current.Resources["DarkGray"];
            Application.Current.Resources["TextBrush"] = Application.Current.Resources["White"];
        }
    }
}
