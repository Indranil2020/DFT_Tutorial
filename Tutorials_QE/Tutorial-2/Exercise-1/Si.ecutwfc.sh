#!/bin/sh

NAME="ecut"
echo " ---------------------------------------------------------------------------------"
echo " |                                                                               |"
echo " |  Please wait calculation is going on at SRMIST-COMET Server. Thank You!!! :)  |"
echo " |                                                                               |"
echo " ---------------------------------------------------------------------------------"

for ecutwfc in  10 15 20 25 30 35 40
do
ecutrho=`expr 4 \* ${ecutwfc}`
cat > ${NAME}_${ecutwfc}.in << EOF

&CONTROL
  		calculation = 'scf' ,
  		     outdir = './' ,
  		     prefix = 'SCF' ,
  		 pseudo_dir = '/opt/home/guest1/upf_files' ,
  		  verbosity = 'low' ,  ! You can use high also to get more informations in the output file.
	      etot_conv_thr = 1.0D-4 ,
/

&SYSTEM
  		      ibrav = 2 ,
                  celldm(1) = 10.2623466921 ,
  		        nat = 2 ,
  		       ntyp = 1 ,
  		    ecutwfc = ${ecutwfc} ,
                    ecutrho = ${ecutrho} ,
  		occupations = 'smearing' ,
                   smearing = 'fermi-dirac' ,
                    degauss = 3.6d-3 ,
/

&ELECTRONS
  		   conv_thr = 1d-6 ,
		mixing_mode = 'plain' ,
  		mixing_beta = 0.7d0 ,
	    diagonalization = 'david' ,
/

ATOMIC_SPECIES
  Si 28.085500d0 Si.pbe-n-kjpaw_psl.0.1.UPF

ATOMIC_POSITIONS {crystal}
  Si   0.00   0.00   0.00
  Si   0.25   0.25   0.25

K_POINTS {automatic}
  6 6 6 1 1 1
EOF

pw.x < ${NAME}_${ecutwfc}.in > ${NAME}_${ecutwfc}.out

done
