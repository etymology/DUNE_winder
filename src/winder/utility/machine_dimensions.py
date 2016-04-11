class WinderMachineDimensions:
   Width_abs_mm = 7091.69
   VerticalHeadSpace_abs_mm = 2800.35
   BottomHeadClearance_abs_mm = 188.75
   ApaInterfaceWidth_abs_mm = 304.29
   ApaSpaceWidth_abs_mm = 6772.01
   SideTransferHeight_abs_mm = 1123.95
   ApaHeight_abs_mm = 2300

   ApaBracketWidth_abs_mm = ( Width_abs_mm - ApaSpaceWidth_abs_mm ) / 2
   ApaWidth_abs_mm = ApaSpaceWidth_abs_mm - ApaInterfaceWidth_abs_mm
   BracketHeight_abs_mm = ApaHeight_abs_mm - SideTransferHeight_abs_mm
   TopHeadClearance_abs_mm = VerticalHeadSpace_abs_mm - ApaHeight_abs_mm - BottomHeadClearance_abs_mm
   ApaSpaceHeight_abs_mm = ApaHeight_abs_mm
   SideTransferWidth_abs_mm = ApaBracketWidth_abs_mm

   Apa_abs_mm = ( ApaWidth_abs_mm, ApaHeight_abs_mm )
   ApaSpace_abs_mm = ( ApaSpaceWidth_abs_mm, ApaSpaceHeight_abs_mm )
   SideTransferSize_abs_mm = ( SideTransferWidth_abs_mm, SideTransferHeight_abs_mm )
   TopTransferSize_abs_mm = ( Width_abs_mm, TopHeadClearance_abs_mm )
   BottomTransferSize_abs_mm = ( Width_abs_mm, BottomHeadClearance_abs_mm )
   BracketSize_abs_mm = ( SideTransferWidth_abs_mm, SideTransferHeight_abs_mm )

class WinderMachinePositions:
   BottomTransfer_start_abs_mm = ( 0, 0 )
   BottomTransfer_end_abs_mm = ( BottomTransfer_start_abs_mm[ 0 ] + WinderMachineDimensions.Width_abs_mm, BottomTransfer_start_abs_mm[ 1 ] + WinderMachineDimensions.BottomHeadClearance_abs_mm )
   LeftTransfer_start_abs_mm = ( BottomTransfer_start_abs_mm[ 0 ], BottomTransfer_end_abs_mm[ 1 ] )
   LeftTransfer_end_abs_mm = ( LeftTransfer_start_abs_mm[ 0 ] + WinderMachineDimensions.SideTransferWidth_abs_mm, LeftTransfer_start_abs_mm[ 1 ] + WinderMachineDimensions.SideTransferHeight_abs_mm )
   RightTransfer_start_abs_mm = ( BottomTransfer_end_abs_mm[ 0 ] - WinderMachineDimensions.SideTransferWidth_abs_mm, LeftTransfer_start_abs_mm[ 0 ] )
   RightTransfer_end_abs_mm = ( BottomTransfer_end_abs_mm[ 0 ], LeftTransfer_end_abs_mm[ 1 ] )
   LeftBracket_start_abs_mm = ( LeftTransfer_start_abs_mm[ 0 ], LeftTransfer_end_abs_mm[ 1 ] )
   LeftBracket_end_abs_mm = ( LeftTransfer_end_abs_mm[ 0 ], LeftBracket_start_abs_mm[ 1 ] + WinderMachineDimensions.BracketHeight_abs_mm )
   RightBracket_start_abs_mm = ( RightTransfer_start_abs_mm[ 0 ], RightTransfer_end_abs_mm[ 1 ] )
   RightBracket_end_abs_mm = ( RightBracket_start_abs_mm[ 0 ], LeftBracket_end_abs_mm[ 1 ] )
   TopTransfer_start_abs_mm = ( BottomTransfer_start_abs_mm[ 0 ], LeftBracket_end_abs_mm[ 1 ] )
   TopTransfer_end_abs_mm = ( BottomTransfer_end_abs_mm[ 0 ], TopTransfer_start_abs_mm[ 1 ] + WinderMachineDimensions.TopHeadClearance_abs_mm )
   Apa_start_abs_mm = ( LeftTransfer_end_abs_mm[ 0 ], LeftTransfer_start_abs_mm[ 1 ] )
   Apa_end_abs_mm = ( RightTransfer_start_abs_mm[ 0 ], TopTransfer_start_abs_mm[ 1 ] )

class WinderTensionHeadDimensions:
   HeadSpaceWidth_abs_mm = 245.9
   HeadWidth_abs_mm = 133.35
   HeadHeight_abs_mm = 152.4
   WireOffset_x_abs_mm = 226.85
   TensionArmLength_abs_mm = 128.78

   HeadSpaceHeight_abs_mm = TensionArmLength_abs_mm + HeadHeight_abs_mm / 2 # Arm is mounted in the center of the Y-dimension.
   TensionArmOffset_x_abs_mm = HeadSpaceWidth_abs_mm - HeadWidth_abs_mm
   TensionArmOffset_y_abs_mm = TensionArmLength_abs_mm - HeadHeight_abs_mm / 2 # Arm is mounted in the center of the Y-dimension.
   TensionHeadWidth_abs_mm = ( HeadSpaceWidth_abs_mm - WireOffset_x_abs_mm ) * 2
   WireOffset_y_abs_mm = HeadSpaceHeight_abs_mm

   TotalWidth_abs_mm = HeadWidth_abs_mm + TensionArmOffset_x_abs_mm

   HeadSpace_abs_mm = ( HeadSpaceWidth_abs_mm, HeadSpaceHeight_abs_mm )

   @staticmethod
   def get_tension_head_box_position( x_pos, y_pos ):
      """
      Gets the tension head bounding box's position given the machine coordinates (which are the coordinates where the wire comes off the tension head).
      """

      x = x_pos - WinderTensionHeadDimensions.HeadSpaceWidth_abs_mm
      y = WinderTensionHeadDimensions.HeadHeight_abs_mm

      return ( x, y )
