import tkinter as tk
from tkinter import ttk
import pandas as pd
import math
from PIL import Image, ImageTk


def display_images():
     # Create a new window to display the images
    image_window = tk.Toplevel(root)
    image_window.title("Images")
    # Load the first image
    image1 = Image.open(r'C:\Users\joaqu\Downloads\plate_and_frame_diagram.png')  # Replace with the path to your first image
    photo1 = ImageTk.PhotoImage(image1)
    label1 = ttk.Label(image_window, image=photo1)
    label1.photo = photo1
    label1.grid(row=0, column=0, padx=5, pady=5)

    # Load the second image
    image2 = Image.open(r'C:\Users\joaqu\Downloads\plate_and_frame_overview_image.png')  # Replace with the path to your second image
    photo2 = ImageTk.PhotoImage(image2)
    label2 = ttk.Label(image_window, image=photo2)
    label2.photo = photo2
    label2.grid(row=0, column=1, padx=5, pady=5)
    
    # # Load the first image
    # image1 = Image.open(r'C:\Users\joaqu\Downloads\plate_and_frame_diagram.png')  # Replace with the path to your first image
    # photo1 = ImageTk.PhotoImage(image1)
    # label1.config(image=photo1)
    # label1.photo = photo1  # Prevent the image from being garbage collected

    # # Load the second image
    # image2 = Image.open(r'C:\Users\joaqu\Downloads\plate_and_frame_overview_image.png')  # Replace with the path to your second image
    # photo2 = ImageTk.PhotoImage(image2)
    # label2.config(image=photo2)
    # label2.photo = photo2  # Prevent the image from being garbage collected

def interpolate_property(property_name, temperature_input):
    try:
        # Convert the 'Temperature' column to numeric
        fluid_properties['Temperature'] = pd.to_numeric(fluid_properties['Temperature'], errors='coerce')

        # Check if the DataFrame is not empty
        if not fluid_properties.empty:
            # Check if the temperature_input is within the available temperature range
            min_temp = fluid_properties['Temperature'].min()
            max_temp = fluid_properties['Temperature'].max()
            if min_temp <= temperature_input <= max_temp:
                # Find the two nearest temperatures in the DataFrame
                lower_temp = fluid_properties['Temperature'][fluid_properties['Temperature'] <= temperature_input].max()
                upper_temp = fluid_properties['Temperature'][fluid_properties['Temperature'] >= temperature_input].min()

                # Get the property values for the two nearest temperatures
                lower_value = fluid_properties.loc[fluid_properties['Temperature'] == lower_temp, property_name].values[0]
                upper_value = fluid_properties.loc[fluid_properties['Temperature'] == upper_temp, property_name].values[0]

                # Linear interpolation
                interpolated_value = lower_value + (upper_value - lower_value) * (temperature_input - lower_temp) / (upper_temp - lower_temp)

                return interpolated_value
            else:
                return None  # Temperature is out of range
        else:
            return None  # DataFrame is empty
    except FileNotFoundError:
        print(f"File not found at {file_path}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Function to perform calculations
def calculate():
    # Retrieve input values from the GUI
    T1 = float(entry_T1.get()) + 273.15
    t1 = float(entry_t1.get()) + 273.15
    Tmi = (T1 + t1) / 2
    tmi = Tmi
    mc = float(entry_mc.get())
    mw = float(entry_mw.get())
    gc = 1
    b = float(entry_b.get())
    L = float(entry_L.get())
    s = float(entry_s.get())
    t = float(entry_t.get())
    Ao = b * L
    A = s * b
    Dh = 2 * s
    Ns = int(entry_Ns.get())
    k = float(entry_k.get())

    if Ns % 2 == 0:
        z = 1
    else:
        z = 0

    if mc < mw:
        TubeC = 1
    else:
        TubeC = 0

    err = 1
    i = 0

    # pw = 0.0  # Initialize pw here
    # kw = 0.0  # Initialize kw here
    # vw = 0.0  # Initialize vw here
    # Cpw = 0.0  # Initialize Cpw here
    # aw = 0.0  # Initialize aw here
    # Prw = 0.0  # Initialize Prw here

    # pc = 0.0  # Initialize pc here
    # kc = 0.0  # Initialize kc here
    # vc = 0.0  # Initialize vc here
    # Cpc = 0.0  # Initialize Cpc here
    # ac = 0.0  # Initialize ac here
    # Prc = 0.0  # Initialize Prc here
    # print(fluid_properties['Temperature'])
    while err > 0.05:
        i += 1

        # if (fluid_properties['Temperature'] == Tmi).any():
                # Warm fluid properties
        pw = 1 / interpolate_property('SpecVolF',tmi)
        kw = interpolate_property('ThermCondF',tmi)
        vw = interpolate_property('viscF',tmi) 
        Cpw = interpolate_property('SpecHeatF',tmi)
        aw = kw / (pw * Cpw)
        Prw = interpolate_property('PrandtlF',tmi)

                # Cold fluid properties
        pc = 1 / interpolate_property('SpecVolF',tmi)
        kc = interpolate_property('ThermCondF',tmi)
        vc = interpolate_property('viscF',tmi) / pc
        Cpc = interpolate_property('SpecHeatF',tmi)
        ac = kc / (pc * Cpc)
        Prc = interpolate_property('PrandtlF',tmi)
        # else:
        #     print(f"No data found for Temperature {Tmi}°C or Temperature {tmi}°C.")



        if z == 1:
            if mc > mw:
                Vw = (mw / (pw * A)) / (Ns / 2)
                Vc = (mc / (pc * A)) / ((Ns + 2) / 2)
            else:
                Vc = (mc / (pc * A)) / (Ns / 2)
                Vw = (mw / (pw * A)) / ((Ns + 2) / 2)
        else:
            Vw = (mw / (pw * A)) / ((Ns + 1) / 2)
            Vc = (mc / (pc * A)) / ((Ns + 1) / 2)

        Rew = (Vw * Dh) / vw
        Rec = (Vc * Dh) / vc

        if Rew < 100:
            Nuw = 1.86 * ((Dh * Rew * Prw / L) ** (1 / 3))
        else:
            Nuw = 0.374 * (Rew ** 0.668) * (Prw ** (1 / 3))

        if Rec < 100:
            Nuc = 1.86 * ((Dh * Rec * Prc / L) ** (1 / 3))
        else:
            Nuc = 0.374 * (Rec ** 0.668) * (Prc ** (1 / 3))

        hi = (Nuw * kw) / Dh
        ho = (Nuc * kc) / Dh

        Uo = ((1 / hi) + (1 / ho) + (t / k)) ** (-1)

        Cw = mw * Cpw
        Cc = mc * Cpc

        if Cw > Cc:
            Cm = Cc
        else:
            Cm = Cw

        N = (Uo * Ao * Ns) / Cm
        F = 1 - (0.0166 * N)

        R = (mc * Cpc) / (mw * Cpw)
        Ec = math.exp((Uo * Ao * Ns * F * (R - 1)) / (mc * Cpc))

        T2C = ((T1 * (R - 1)) - (R * t1 * (1 - Ec))) / ((R * Ec) - 1)
        t2C = t1 + ((T1 - T2C) / R)

        Tavenew = (T2C + T1) / 2
        errw = abs(Tmi - Tavenew) / (Tmi - 273.15)

        tavenew = (t2C + t1) / 2
        errc = abs(tmi - tavenew) / (Tmi - 273.15)

        err = max(errc, errw)
        Tmi = Tavenew
        tmi = tavenew

        LMTDC = ((T1 - t2C) - (T2C - t1)) / math.log((T1 - t2C) / (T2C - t1))

        qwc = mw * Cpw * (T1 - T2C)
        qcc = mc * Cpc * (t2C - t1)

        qc = Uo * Ao * Ns * F * LMTDC # total heat transfer

        Rdi = 3.52E-6
        Rdo = 3.52E-6
        U = ((1 / Uo) + Rdi + Rdo) ** (-1)

        Nf = (U * Ao * Ns) / Cm
        Ff = 1 - (0.0166 * Nf)

        Ecf = math.exp((U * Ao * Ns * Ff * (R - 1)) / (mc * Cpc))

        T2Cf = ((T1 * (R - 1)) - (R * t1 * (1 - Ecf))) / ((R * Ecf) - 1)
        t2Cf = t1 + ((T1 - T2Cf) / R)
        T=(T2Cf+t2Cf)/2
        if T1 - t2Cf > 0:
            LMTDCf = ((T1 - t2Cf) - (T2Cf - t1)) / math.log((T1 - t2Cf) / (T2Cf - t1))
        else:
            # Handle the case when (T1 - t2Cf) is not greater than zero
            LMTDCf = 0  # or set it to a meaningful value for your application
    # Inside the `calculate` function, after your calculations

    # Update the label for Outlet Temperature of warm fluid
    label_T2C.config(text=f"Outlet Temperature of warm fluid(°C): {T2C:.2f}")

    # Update the label for Outlet Temperature of cold fluid
    label_t2C.config(text=f"Outlet Temperature of cold fluid(°C): {t2C:.2f}")

    # Update the label for Overall Heat Transfer Rate
    label_qc.config(text=f"Overall Heat Transfer Rate(J/s): {qc:.2f}")

    # Update the label for Overall Convection Coefficient
    label_Uo.config(text=f"Overall Convection Coefficient(W/(m^2 K)): {Uo:.2f}")

    # Update the label for Outlet Temperature of Warm Fluid After 1 Year
    label_T2Cf.config(text=f"Outlet Temperature of Warm Fluid After 1 Year(°C): {T2Cf:.2f}")

    # Update the label for Outlet Temperature of Cold Fluid After 1 Year
    label_t2Cf.config(text=f"Outlet Temperature of Cold Fluid After 1 Year(°C): {t2Cf:.2f}")

    # Update the label for Overall Heat Transfer Rate After 1 Year
    label_qcf.config(text=f"Overall Heat Transfer Rate After 1 Year(kJ): {qc:.2f}")

    # You should have the variables T2C, t2C, qc, Uo, T2Cf, t2Cf available from your calculations.



'''this is for the code for the gui: tkinter is the application'''

# Read the Excel file with fluid properties
file_path = r'c:\Users\joaqu\Downloads\Water_props.xlsx'
fluid_properties = pd.read_excel(file_path)

# print(fluid_properties)
root = tk.Tk()
root.title("Heat Exchanger Calculator")

# # Create a frame to hold the images
# frame = ttk.Frame(root)
# frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

# # Create labels for the images
# label1 = ttk.Label(frame)
# label1.grid(row=0, column=0, padx=5, pady=5)
# label2 = ttk.Label(frame)
# label2.grid(row=0, column=1, padx=5, pady=5)

#rest of the GUI
input_frame = ttk.Frame(root)
input_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")

label_T1 = ttk.Label(input_frame, text="T1 (°C):")
label_T1.grid(row=0, column=0, padx=5, pady=5)
entry_T1 = ttk.Entry(input_frame)
entry_T1.grid(row=0, column=1, padx=5, pady=5)

label_t1 = ttk.Label(input_frame, text="t1 (°C):")
label_t1.grid(row=1, column=0, padx=5, pady=5)
entry_t1 = ttk.Entry(input_frame)
entry_t1.grid(row=1, column=1, padx=5, pady=5)

label_mw = ttk.Label(input_frame, text="Mass Flow Rate of Warm Fluid(kg/s):")
label_mw.grid(row=2, column=0, padx=5, pady=5)
entry_mw = ttk.Entry(input_frame)
entry_mw.grid(row=2, column=1, padx=5, pady=5)

label_mc = ttk.Label(input_frame, text="Mass Flow Rate of Cold Fluid(kg/s):")
label_mc.grid(row=3, column=0, padx=5, pady=5)
entry_mc = ttk.Entry(input_frame)
entry_mc.grid(row=3, column=1, padx=5, pady=5)

label_b = ttk.Label(input_frame, text="Plate Width(m):")
label_b.grid(row=4, column=0, padx=5, pady=5)
entry_b = ttk.Entry(input_frame)
entry_b.grid(row=4, column=1, padx=5, pady=5)

label_L = ttk.Label(input_frame, text="Plate Height(m):")
label_L.grid(row=5, column=0, padx=5, pady=5)
entry_L = ttk.Entry(input_frame)
entry_L.grid(row=5, column=1, padx=5, pady=5)

label_s = ttk.Label(input_frame, text="Plate Spacing(m):")
label_s.grid(row=6, column=0, padx=5, pady=5)
entry_s = ttk.Entry(input_frame)
entry_s.grid(row=6, column=1, padx=5, pady=5)

label_t = ttk.Label(input_frame, text="Plate Thickness(m):")
label_t.grid(row=7, column=0, padx=5, pady=5)
entry_t = ttk.Entry(input_frame)
entry_t.grid(row=7, column=1, padx=5, pady=5)

label_Ns = ttk.Label(input_frame, text="Number of Plates:")
label_Ns.grid(row=8, column=0, padx=5, pady=5)
entry_Ns = ttk.Entry(input_frame)
entry_Ns.grid(row=8, column=1, padx=5, pady=5)

label_k = ttk.Label(input_frame, text="Thermal Conductivity of Plate(W/mK):")
label_k.grid(row=9, column=0, padx=5, pady=5)
entry_k = ttk.Entry(input_frame)
entry_k.grid(row=9, column=1, padx=5, pady=5)

#button to display images
display_button = ttk.Button(root, text="Display Images", command=display_images)
display_button.grid(row=10, column=0, padx=10, pady=10)
# image = Image.open(r'C:\Users\joaqu\Downloads\plate_and_frame_diagram.png') #path for the image 1
# photo = ImageTk.PhotoImage(image) #definition of the photo variable
# label_image.config(image=photo) #places image in tkinter
# label_image.image = photo #tkinter

# image2 = Image.open(r'C:\Users\joaqu\Downloads\plate_and_frame_overview_image.png') #path for the image 2
# photo2 = ImageTk.PhotoImage(image) #definition of the photo variable
# label_image2.config(image=photo) #places image in tkinter
# label_image2.image = photo #tkinter

calculate_button = ttk.Button(input_frame, text="Calculate", command=calculate)
calculate_button.grid(row=10, columnspan=2, padx=5, pady=10)

output_frame = ttk.Frame(root)
output_frame.grid(row=1, column=0, padx=10, pady=10, sticky="w")

label_T2C = ttk.Label(output_frame, text="Outlet Temperature of warm fluid(°C):")
label_T2C.grid(row=0, column=0, padx=5, pady=5)

label_t2C = ttk.Label(output_frame, text="Outlet Temperature of cold fluid(°C):")
label_t2C.grid(row=1, column=0, padx=5, pady=5)

label_qc = ttk.Label(output_frame, text="Overall Heat Transfer Rate(J/s):")
label_qc.grid(row=2, column=0, padx=5, pady=5)

label_Uo = ttk.Label(output_frame, text="Overall Convection Coefficient(W/(m^2 K)):")
label_Uo.grid(row=3, column=0, padx=5, pady=5)

label_T2Cf = ttk.Label(output_frame, text="Outlet Temperature of Warm Fluid After 1 Year(°C):")
label_T2Cf.grid(row=4, column=0, padx=5, pady=5)

label_t2Cf = ttk.Label(output_frame, text="Outlet Temperature of Cold Fluid After 1 Year(°C):")
label_t2Cf.grid(row=5, column=0, padx=5, pady=5)

label_qcf = ttk.Label(output_frame, text="Overall Heat Transfer Rate After 1 Year(kJ):")
label_qcf.grid(row=6, column=0, padx=5, pady=5)

root.mainloop()
