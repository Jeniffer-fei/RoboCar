
//==============================================================================
// Nome: Jeniffer Nicolly Valentim Nunes
// Mecatrônica - Noturno – 4k
// Trabalho de Conclusão de Curso Mecatrônica
// Projeto: Carrinho de "controle remoto " DJLVL
//==============================================================================
#include <servo.h>
    sbit IN1 at PORTA.B1;
    sbit IN2 at PORTA.B2;
    sbit servo1 at PORTA.B3;

   int s1;

   void ligaservo() {
   servo1=1;
   servo_pos(s1);
   servo1=0;
   delay_ms(20); // INTERVALO ENTRE PULSOS
   }
    void frente()
    {
     IN1=1;
     IN2=0;
    }
    void re()
     {
     IN1=0;
     IN2=1;
     }
     void parar()
     {
     IN1=1;
     IN2=1;
     }
//===============================================================================                                PROGRAMA PRINCIPAL
//===============================================================================
void main (void)
{
// variaveis
char comando;
// Registradores de Configuração:

        ADCON1 = 0b00001111;
        CMCON = 0b00000111;

// Configuração dos PORTS de Entrada e Saida
// 0 -> configura o BIT como Saída
// 1 -> configura o BIT como Entrada
// Exemplo:  TRISA = 0b00001111;

  TRISD = 0b00000000;
  TRISB = 0b00000000;
  TRISC = 0b10000000;
  TRISA = 0b00000000;
 
  PORTA = 0b11111111;

  s1=90; // Valor posição Zero do Servo
 UART1_Init(9600);
  delay_ms(500);
//******************************************************************************
//Início do Loop principal
//******************************************************************************
  while (1)
  {
     if(UART1_Data_Ready())
     {
     comando = UART1_Read();
      if (comando == 'F')
      {
      frente ();
      }
       else
       if (comando == 'B')
      {
      re();
      }

       if (comando == 'S')
      {
      parar();
      }

        if(comando=='L')
      {
        s1=s1+5;
        if(s1>=180)
        {
         s1=180;
        }
      }
      if(comando=='R')
      {
        s1=s1-5;
        if(s1<=30)
        {
          s1=30;
        }
        }
       if(comando=='G')
      {
        s1=s1+5;
        frente ();
        if(s1>=180)
        {
         s1=180;
        }
        }
      if(comando=='I')
      {
        s1=s1-5;
        frente ();
        if(s1<=30)
        {
          s1=30;
        }
        }
         if(comando=='H')
      {
        s1=s1+5;
        re ();
        if(s1>=180)
        {
         s1=150;
        }
        }
      if(comando=='J')
      {
        s1=s1-5;
        re ();
        if(s1<=30)
        {
          s1=30;
        }
      }
      }
    ligaservo();
   }
}
