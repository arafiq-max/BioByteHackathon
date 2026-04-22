# BioByteHackathon

We are all students at UC San Diego who have experienced long walks across campus, often in high heat and without enough time to access water. Prolonged exposure to heat can lead to serious health risks, including dehydration, heat stress, and increased vulnerability to illness.
At a larger scale, these challenges highlight systemic gaps in urban planning, particularly the lack of sufficient green spaces that provide cooling through shade and CO₂ absorption. Given UCSD’s large infrastructure and environmental footprint, improving campus design using data-driven insights can significantly impact both student health and climate resilience.
This motivated us to develop Biobyte, a wearable, data-driven system that monitors real-time heat exposure as students move across campus. Biobyte integrates hardware, environmental data, and machine learning to identify areas where students experience excessive heat and limited vegetation.

Biobyte consists of four key components: Wearable sensing hardware (Arduino + temperature sensor), GPS tracking via a mobile device, Satellite-derived green-space data, and a machine-learning pipeline for environmental analysis. 

The wearable device measures ambient temperature using a Modulino Thermo sensor mounted on a 3D-printed armband. This data is transmitted to a web application built using Python and HTML, where it is combined with GPS data and environmental datasets. Additionally, we developed a Python-based script to process satellite imagery and classify green spaces across campus by analyzing color and shading patterns. This enables us to map vegetation density and correlate it with temperature exposure. To move beyond simple data collection, we developed a machine learning pipeline that processes Scripps Research datasets, including temperature, humidity, GPS location, and green space distribution.

The pipeline performs several key steps:
Cleans and aligns data from multiple CSV sources
Creates meaningful features such as temperature-humidity interactions, time-based trends, and rolling averages
Uses a Random Forest model to identify relationships between environmental conditions and heat exposure
Estimates heat exposure levels and identifies high-risk zones (“heat hotspots”) across campus

By integrating sensing, environmental data, and machine learning, Biobyte can:
Track real-time temperature exposure across campus
Identify locations with excessive heat and low vegetation
Analyze how environmental factors (humidity, time of day, green space) influence heat exposure
Provide data-driven recommendations for improving green space distribution
This transforms raw environmental data into actionable intelligence for campus planning and public health!
