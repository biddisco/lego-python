import sys
import usb.core
import usb.util

dev = usb.core.find(find_all=True)

for cfg in dev:
  print 'Decimal VendorID=' + str(cfg.idVendor) 
  sys.stdout.write('Decimal VendorID=' + str(cfg.idVendor) + ' & ProductID=' + str(cfg.idProduct) + '\n')
  sys.stdout.write('Hexadecimal VendorID=' + hex(cfg.idVendor) + ' & ProductID=' + hex(cfg.idProduct) + '\n\n')

