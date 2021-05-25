<?php
//Main-----------------------------------------------------------------------------
if (($argc >= 1) && ($argc <= 2)) // Argument check
{
    if ($argc == 2) 
    {
        if (strcmp($argv[1],"--help") == 0)
        {
            help();
            exit(0);
        }
        else
        {
            fprintf (STDERR, "Wrong arguments\n");
            die(10);
        }
    }
}
else
{
    fprintf (STDERR, "Wrong arguments\n");
    die(10);
}

/*
*processing input text in input() function -> comment trimming, white spaces remove,..
*first_line() checks header of input string
*variable array_top contains
*/
$stripped_string = input();
first_line($stripped_string[0]);
$array_top = count($stripped_string);

/*
*Instruction check and instruction parameters check
*/
for($i=1; $i < $array_top ;$i++)
{
    parser($stripped_string[$i]);
}

/*
*Final output printout
*First of all print xml header
*then print instructions in xml format with generator() in cycle
*/
echo ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n");
echo ("<program language=\"IPPcode21\">\n");
$countrik = 1;
for($i=1; $i < $array_top ;$i++) 
{
    generator($stripped_string[$i]);
    $countrik++;
}
echo ("</program>\n");
//End of Main---------------------------------------------------------------------------------

/*
*Help
*/
function help()
{
    echo ("------------------------------------------------------------------------\n");
    echo ("Skript typu filtr (parse.php v jazyce PHP 7.4) načte ze standardního\n");
    echo ("vstupu zdrojový kód v IPPcode21, zkontroluje lexikální a syntaktickou\n");
    echo ("správnost kódu a vypíše na standardní výstup XML reprezentaci programu\n");
    echo ("dle specifikace v sekci.\n");
    echo ("Parametry programu:\n");
    echo ("--help : vypíše na standardní vstup nápovědu\n");
    echo ("-----------------------------------------------------------------------\n");
}


/*
*Input processing, trimming, filtering
*/
function input()
{
    if(($input_string = file_get_contents('php://stdin')) == FALSE) //File open check
    {
        fprintf (STDERR, "File open error\n");
        die(11); 
    }

    $input_string = explode(PHP_EOL, $input_string); //split text by ends of lines
    $array_top = count($input_string); //count of array elements

    for($i=0; $i < $array_top ;$i++) //commentary trimming
    {
        $input_string[$i] = trim_comments($input_string[$i]);
    }

    $input_string = array_filter($input_string, 'strlen'); //erase empty lines
    $input_string = array_values($input_string);// repair indexes 

    $array_top = count($input_string);
    for($i=0; $i < $array_top ;$i++)//trim white symbols from begin and end of strings
    {
        $input_string[$i] = trim($input_string[$i]);
    }

    return $input_string;
}

/*
*First line check
*First line must be ".ippcode21" and it is CASE INSENSITIVE
*/
function first_line($line)
{
    $line = strtolower($line);
    if($line != ".ippcode21")
    {
        fprintf (STDERR, "Wrong header\n");
        die(21);
    }
}

/*
*Trim comments with regular expression
*/
function trim_comments($input_string) 
{
    $comment_killed = preg_replace('/#.*/',"",$input_string);
    return $comment_killed;
}

/*
*Argument check of Variable from .IPPCode21
*/
function variable($var) 
{
    $aux = preg_match('/^(GF|LF|TF)@([a-zA-Z]|-|_|\*|\$|\%|\&|\!|\?)([a-zA-Z0-9]|-|_|\*|\$|\%|\&|\!|\?)*$/', $var); 
    if ($aux == 0)
    {
        fprintf (STDERR, "Lexical or Syntax error\n");
        die(23);
    }
}

/*
*Argument check of Symbol from .IPPCode21
*/
function symbol($sym) 
{
    $aux = explode("@", $sym);

    if(preg_match('/^(int|string|bool|nil)@.*$/', $sym) == 1)
    {

        if ($aux[0] == "int")
        {
            if ($aux[1] == "")
            {
                fprintf (STDERR, "Lexical or Syntax error\n");
                die(23);
            }
            else return 101;
        }

        elseif ($aux[0] == "bool")
        {
            if ((preg_match('/^(true|false)$/', $aux[1]) == 0))
            {
                fprintf (STDERR, "Lexical or Syntax error\n");
                die(23);
            }
            else return 102;
        }
        elseif ($aux[0] == "string")
        {
            if ((preg_match('/^([^\s#\\\\]|\\\\[0-9]{3})+$/', $aux[1]) == 0)) 
            {
                fprintf (STDERR, "Lexical or Syntax error\n");
                die(23);
            }
            else return 103;
        }
        elseif ($aux[0] == "nil")
        {
            if ((preg_match('/^(nil)$/', $aux[1]) == 0))
            {
                fprintf (STDERR, "Lexical or Syntax error\n");
                die(23);
            } 
            else return 104;
        }
    }
    elseif ((preg_match('/^(GF|LF|TF)@([a-zA-Z]|-|_|\*|\$|\%|\&|\!|\?)([a-zA-Z0-9]|-|_|\*|\$|\%|\&|\!|\?)*$/', $sym) == 1))
    {
        variable($sym);
        return 105;
    }
   # elseif ((preg_match('/^(int|string|bool)$/', $sym) == 1))
   # {
   #     return 106;
   # }
    else 
    {
        fprintf (STDERR, "Lexical or Syntax error\n");
        die(23);
    }
    
}

/*
*Argument check of Label from .IPPCode21
*/
function label($lab)
{
    $aux = preg_match('/^([a-zA-Z]|-|_|\*|\$|\%|\&|\!|\?)([a-zA-Z0-9]|-|_|\*|\$|\%|\&|\!|\?)*$/', $lab);
    if ($aux == 0)
    {
        fprintf (STDERR, "Lexical or Syntax error\n");
        die(23);
    }
    else return 107;
}

/*
*Argument check of Type from .IPPCode21
*/
function type($typ)
{
    $aux = preg_match('/^(int|string|bool|nil)$/', $typ);
    if ($aux == 0)
    {
        fprintf (STDERR, "Lexical or Syntax error\n");
        die(23);
    }
}


/*
*Instruction check
*Check number of arguments for given instruction
*Check correctness of arguments with functions variable(),symbol(),label(),type()
*/
function parser($line)
{
    $line = explode(" ", $line); //split lines by spaces to seperate instruction from remaining text
    $line[0] = strtoupper($line[0]);
    if (count($line) >= 1 && count($line) <= 4)
    {
        //switch for instructions
        switch($line[0]) 
        {
        case 'MOVE':
        case 'INT2CHAR':
        case 'TYPE':
        case 'STRLEN':
            if(count($line)== 3){
            variable($line[1]);
            symbol($line[2]);
            } else {
                fprintf (STDERR, "Lexical or Syntax error\n");
                die(23);
            } 
            break;
        case 'CREATEFRAME':
        case 'PUSHFRAME':
        case 'POPFRAME':
        case 'RETURN':
        case 'BREAK':
            if(count($line)== 1){
            }else{
                fprintf (STDERR, "Lexical or Syntax error\n");
                die(23);
            } 
            break;
        case 'DEFVAR':
        case 'POPS':
            if(count($line)== 2){
                variable($line[1]);
            } else {
                fprintf (STDERR, "Lexical or Syntax error\n");
                die(23);
            } 
            break;      
        case 'CALL':
        case 'JUMP':
        case 'LABEL':
            if(count($line)== 2){
                label($line[1]);
            } else {
                fprintf (STDERR, "Lexical or Syntax error\n");
                die(23);
            } 
            break;      
        case 'PUSHS':
        case 'WRITE':
        case 'EXIT':
        case 'DPRINT':
            if(count($line)== 2){
                symbol($line[1]);
            } else {
                fprintf (STDERR, "Lexical or Syntax error\n");
                die(23);
            } 
            break;            
        case 'ADD':
        case 'SUB':
        case 'MUL':
        case 'IDIV':    
        case 'LT':
        case 'GT':
        case 'EQ':
        case 'AND':
        case 'OR':
        case 'NOT':
        case 'STRI2INT':
        case 'CONCAT':
        case 'GETCHAR':
        case 'SETCHAR':
            if(count($line)== 4){
                variable($line[1]);
                symbol($line[2]);
                symbol($line[3]);
            } else {
                fprintf (STDERR, "Lexical or Syntax error\n");
                die(23);
            } 
            break;                      
        case 'JUMPIFEQ':
        case 'JUMPIFNEQ':    
            if(count($line)== 4){
                label($line[1]);
                symbol($line[2]);
                symbol($line[3]);
            } else {
                fprintf (STDERR, "Lexical or Syntax error\n");
                die(23);
            } 
            break;
        case 'READ':
            if(count($line)== 3){
                variable($line[1]);
                type($line[2]);
            } else {
                fprintf (STDERR, "Lexical or Syntax error\n");
                die(23);
            } 
            break;                
        default:
        fprintf (STDERR, "Wrong code in IPPcode21\n");
        die(22);
        break;
        }
    } 
    else
    {
        fprintf (STDERR, "Wrong code in IPPcode21\n");
        die(22);
    } 
}

/*
*Generation of instructions in XML representation
*/
function generator($stripped_string)
{
    $line = explode(" ", $stripped_string); 
    $counter = count($line);
    global $countrik;
    echo ("  <instruction order=\"$countrik\" opcode=\"$line[0]\">\n");

    for($j=1; $j < $counter ;$j++) 
    {
        $arg = symgen($line[$j]);//assist function for type in XML representation
    
        switch ($arg) 
        {
            case 101:
                $arg = "int";
                $help = explode("@", $line[$j]);
                $line[$j] = $help[1];
                break;
            case 102:
                $arg = "bool";
                $help = explode("@", $line[$j]);
                $line[$j] = $help[1];
                break;
            case 103:
                $arg = "string";
                $help = explode("@", $line[$j]);
                unset($help[0]);
                $help = implode($help);
                $help = preg_replace('/\&/',"&amp;",$help);
                $help = preg_replace('/\</',"&lt;",$help);
                $help = preg_replace('/\>/',"&gt;",$help);
                $line[$j] = $help;
                break;
            case 104:
                $arg = "nil";
                $help = explode("@", $line[$j]);
                $line[$j] = $help[1];
                break;
            case 105:
                $arg = "var";
                break;
            case 106:
                $arg = "type";
                break;
            default:
                $arg = "label";
        }
        echo ("    <arg$j type=\"$arg\">$line[$j]</arg$j>\n");
    }
    echo ("  </instruction>\n");

}

/*
*Assist function for generator() which checks type in XML representation
*return codes 101-106 are used in generator() to determine XML representation output
*/
function symgen($sym)
{
    $aux = explode("@", $sym);

    if(preg_match('/^(int|string|bool|nil)@.*$/', $sym) == 1)
    {

        if ($aux[0] == "int")
        {
            if ($aux[1] == "")
            {
                return 666; //return random number which will never be used
            }
            else return 101;
        }

        elseif ($aux[0] == "bool")
        {
            if ((preg_match('/^(true|false)$/', $aux[1]) == 0))
            {
                return 666;
            }
            else return 102;
        }
        elseif ($aux[0] == "string")
        {
            if ((preg_match('/^([^\s#\\\\]|\\\\[0-9]{3})+$/', $aux[1]) == 0))
            {
                return 666;
            }
            else return 103;
        }
        elseif ($aux[0] == "nil")
        {
            if ((preg_match('/^(nil)$/', $aux[1]) == 0))
            {
                return 666;
            } 
            else return 104;
        }
    }
    elseif ((preg_match('/^(GF|LF|TF)@.*$/', $sym) == 1))
    {
        variable($sym);
        return 105;
    }
    elseif ((preg_match('/^(int|string|bool)$/', $sym) == 1))
    {
        return 106;
    }
    else 
    {
        return 666;
    }   
}
?>
