import cv2
import numpy as np

# read field view
image = cv2.imread( "new1.png")

# convert to gray
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# binary thresholding
# ~ kernel_size = 3
# ~ ret,thresh = cv2.threshold(image,200,255,cv2.THRESH_BINARY)  

# get contours 
# contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

# ~ # get only line  contours( and not image contours at [0][0] )
# ~ contours = contours[0][1]
# ~ print('Quick position ->', contours[1])

# window
window = 'Field view'

# ~ #drawing Contours
# ~ radius =0
# ~ color = (30,255,50)
# ~ cv2.drawContours(image, contours, -1, color , radius)
cv2.imshow(window, image)
# ~ cv2.waitKey(0)
# ~ #close
# ~ cv2.destroyAllWindows() 
  
