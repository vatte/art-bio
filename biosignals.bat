@ECHO on
call C:\Users\MTG-user\anaconda3\Scripts\activate.bat activate art-bio
cd C:\Users\MTG-user\Desktop\art-bio-biosignalsplux
python art-bio.py -d biosignalsplux -c reeg ws -c recg ws -c reda ws -c reeg file -c recg file -c reda file --filename readings.txt
PAUSE