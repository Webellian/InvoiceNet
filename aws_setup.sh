# Clone
git clone https://github.com/Webellian/InvoiceNet.git
cd InvoiceNet/
git checkout pl_parsers

# Run installation script
sudo apt-get install -y python-virtualenv
./install.sh

# Source virtual environment
source env/bin/activate


#Test DNN
#nvcc -V
#from tensorflow.python.client import device_lib
#device_lib.list_local_devices()

#monitoring
htop
watch -n 0.5 nvidia-smi

# Retrain parsers
cd invoicenet/parsing
python amount_generator.py
python date_generator.py
cd ../..
python train_parser.py --field amount --batch_size 8
python train_parser.py --field date --batch_size 8


# Train
# Make sure data is copied to data/ directory
# Make sure invoicenet/__init__.py has correct fields
python prepare_data.py --data_dir data/
./jap_20210513_postprocess_data.sh

python train.py --field bank_account --batch_size 32 --early_stop_steps 200 --restore

# Predict
python predict.py --field gross_amount --data_dir data --pred_dir predictions
python predict.py --field net_amount --data_dir data --pred_dir predictions
python predict.py --field issued_on sale_date date_of_payment --data_dir data --pred_dir predictions
python predict.py --field payment_term --data_dir data --pred_dir predictions
python predict.py --field document_number --data_dir data --pred_dir predictions

python predict.py --field payment_term --data_dir data --pred_dir predictions && ./jap_20210427_json_to_tsv.sh && code predictions.tsv


python predict.py --field document_number contractor tax_number bank_account issued_on sale_date date_of_payment payment_term currency net_amount gross_amount vat --data_dir data --pred_dir predictions
./jap_20210611_validate.sh
