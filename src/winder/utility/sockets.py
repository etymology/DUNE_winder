def socket_file_readlines( socket_file ):
   result = []

#    while True:
#       line = socket_file.readline()
#       if line is None:
#          break
#       else:
#          result.append( line )

   result.append( socket_file.readline() )

   return result
