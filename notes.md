# Notes

## Day 1

I live in Almaty, and the air here gets really bad in winter. That's why I wanted to do a project about local air pollution.

CHP-2 is a large power and heating plant that burns coal. It's being converted to gas, with completion planned for the end of 2026. This should reduce pollution from the plant, but I want to see how much difference it makes to the city's air. Weather matters too, so a cleaner winter could partly be the result of different weather conditions.

My first goal is to see if machine learning can predict tomorrow's PM2.5 levels. Later, I'd like to look at data from before and after the switch to gas, taking weather into account.

I created the repository and uploaded the scripts for downloading weather data, CAMS forecasts, and PM2.5 measurements from the US Embassy station through OpenAQ.
## Day 2

I ran all three download scripts. The data is now on my computer.

- Weather: 53,472 hourly rows, about 6 years of data.
- CAMS forecast: 36,816 hourly rows. The data starts in August 2022.
- US Embassy PM2.5: 37,822 hourly rows, from April 2020 to November 2025.

There were no PM2.5 rows for 2026. The embassy station stopped working on 14 November 2025, so this source won't cover 2026.

The median PM2.5 was 15 µg/m³ and the average was about 30. The highest hourly value was 421 on 19 January 2021. The WHO guideline is 15 µg/m³ for a daily average, so I need to calculate daily averages to compare them.

I plan to use the available data from 2020-2025 for training. CAMS will only cover the part from August 2022 onward. For the 2026 CHP-2 analysis and demo, I'll need another PM2.5 source. I might use AirGradient sensors in Almaty.

I left the data files out of GitHub because they're large. Anyone can download them by running the scripts.
## Day 3

I used `build_dataset.py` to put weather, CAMS and PM2.5 data into one hourly table. I kept every hour, even when there was no data, so the gaps are easy to see. I also removed values below 0 or above 1000.

About 34% of PM2.5 data is missing. In 2021–2022, around 45% is missing, but in 2024, it’s only about 5%. There’s no data for 2026 because the embassy station stopped working.

In winter, PM2.5 is highest at 15:00 and lowest at 6:00. I thought it would be worst in the evening, so this was surprising. I checked nearby Clarity sensors, and they showed the same pattern. Maybe daytime winds carry polluted air uphill from the lower parts of the city.
## Day 4

I made the first plots in `01_eda.ipynb`. Winter PM2.5 is about 6 times higher than in summer. The average is around 70 µg/m³ in January and 67 in December, compared to 10–12 in summer.
During the heating season, weekdays and weekends look almost the same, with averages around 50–55 µg/m³. This suggests traffic may not be the main cause of winter smog.
The 10 most polluted days were all in December or January, between 2020 and 2023. Daily averages were 170–222 µg/m³. It was cold, from -6 to -14 °C, and the boundary layer was only about 25–70 m high, leaving little room for pollution to spread. The wind wasn’t always weak, so cold weather and poor air mixing may explain more than wind speed alone.



## Day 5

I compared PM2.5 with the weather. Daily PM2.5 had the strongest correlation with temperature (-0.65), followed by boundary layer height, or BLH (-0.51). Wind had almost no correlation (0.03). BLH tells us how high the air can mix. When it’s low, pollution can stay trapped near the ground. The median line on the plot also shows lower PM2.5 as BLH gets higher.

PM2.5 usually rises around the start of heating, roughly 15 October. It went from 25 to 31 µg/m³ in 2020, from 14 to 20 in 2023, and from 18 to 31 in 2025. The change was small in 2022 and 2024, and there’s no data for 2021. Colder weather could explain part of the increase too.

## Day 6

I compared CAMS forecasts with the measured PM2.5. In winter (December–February), CAMS gave an average of about 34 µg/m³, while the measurements averaged 61. The bias was -27 µg/m³ and the MAE was about 40. Most winter points on the scatter plot were below the red line, so CAMS often missed how bad the pollution actually was.

In summer, the forecasts were much closer to the measurements. The MAE was about 6 µg/m³, and CAMS was slightly too high on average, with a bias of +3.

The biggest errors were in winter, when Almaty has its worst smog. That’s where I want my model to improve the forecasts most
## Day 7

I wrote what I learned in the notebook and updated the README. I added two things about the data: the time zone change in March 2024 and missing BLH data for January–June 2024. I also added two plots to the README: PM2.5 by month and the daily cycle
##day 8

made features.py to turn hourly data into one row per day with 38 features

the model predicts tomorrow's average PM2.5 using data available by midnight

the strongest feature is PM2.5 at 23:00 today which makes sense because bad air late at night often carries over into the next day

tomorrow's weather comes from actual recorded data so it works like a perfect forecast real forecasts can be wrong so the results may look better than they would in practice
