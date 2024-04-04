import argparse
import configparser
import mysql.connector
import os

parser = argparse.ArgumentParser(
  prog='pdns-tsig-from-catalog for PowerDNS',
  description='Sets the TSIG Key from catalog zone to the member zones')

parser.add_argument(
   '--config',
   dest='config',
   required=True,
   help='powerdns config file, that inlcudes mysql login')
args = parser.parse_args()


config = configparser.ConfigParser()
with open(args.config, 'r') as f:
    config_string = '[default]\n' + f.read()
config.read_string(config_string)

mydb = mysql.connector.connect(
  host=config["default"]["gmysql-host"],
  user=config["default"]["gmysql-user"],
  password=config["default"]["gmysql-password"],
  database=config["default"]["gmysql-dbname"]
)

mycursor = mydb.cursor(dictionary=True)
mycursor.execute("DROP VIEW IF EXISTS `domainmetadata_tsig`")
mycursor.execute("CREATE VIEW domainmetadata_tsig AS SELECT * FROM domainmetadata WHERE `kind`='TSIG-ALLOW-AXFR' OR `kind`='AXFR-MASTER-TSIG';")
mycursor.execute("SELECT d.`id`,d.`name`,d.`catalog`,(CASE WHEN dm.`kind` != '' THEN dm.`kind` ELSE NULL END) as kind FROM domains AS d LEFT JOIN domainmetadata_tsig AS dm ON d.id = dm.domain_id WHERE d.`type` NOT IN ('PRODUCER','CONSUMER');")

domainlist = mycursor.fetchall()

catalog = mydb.cursor(dictionary=True)

for domain in domainlist:
  if(domain["kind"] == None and domain["catalog"] != None):
    catalog.execute("SELECT d.`name`,d.`type`,dm.`content` FROM `domains` AS d RIGHT JOIN domainmetadata AS dm ON d.id=dm.domain_id WHERE (`kind`='TSIG-ALLOW-AXFR' OR `kind`='AXFR-MASTER-TSIG') and name='"+ domain["catalog"]+"';");
    cout = catalog.fetchone()
    if(cout["type"] == "PRODUCER"): type = "primary"
    if(cout["type"] == "CONSUMER"): type = "secondary"
    os.system("pdnsutil activate-tsig-key "+ domain["name"] + " "+ cout["content"] + " " + type)
