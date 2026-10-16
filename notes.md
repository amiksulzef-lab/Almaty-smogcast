# Notes
## Day 1

I live in Almaty, and the air here gets really bad in winter. That's why I wanted to do a project about local air pollution.

CHP-2 burns coal to produce electricity and heat. It is being converted to gas, and the plan is to finish the work by the end of 2026. This should reduce pollution from the plant. I want to see how much difference it makes to the city's air. Weather matters too, so if the air gets cleaner, part of the change could be because of the weather.

My first goal is to predict tomorrow's average PM2.5 using machine learning. Later, I want to compare the data before and after the switch to gas, taking weather into account.

I created the repository and added scripts to download weather data, CAMS forecasts and PM2.5 measurements from the US Embassy station through OpenAQ.

## Day 2

I ran all three download scripts. The data is now on my computer.

- Weather: 53,472 hourly rows, about 6 years of data.
- CAMS forecast: 36,816 hourly rows, starting in August 2022.
- US Embassy PM2.5: 37,822 hourly rows, from April 2020 to November 2025.

There are no embassy PM2.5 rows for 2026. The station stopped working on 14 November 2025, so this source won't cover that year.

The median hourly PM2.5 was 15 µg/m³, and the average was about 30. The highest hourly value was 421 µg/m³ on 19 January 2021. The WHO guideline is 15 µg/m³ for a daily average. I need to calculate daily averages to compare the measurements with it.

I plan to use the available data from 2020-2025 for training. CAMS will only cover the part from August 2022 onward. For the 2026 CHP-2 analysis and demo, I need another PM2.5 source. I might use AirGradient sensors in Almaty.

I left the data files out of GitHub because they're large. Anyone can download them by running the scripts.

## Day 3

I used `build_dataset.py` to put weather, CAMS and PM2.5 data into one hourly table. I kept hours with missing data too, so the gaps are easy to see. I also removed PM2.5 values below 0 or above 1000 µg/m³.

About 34% of the PM2.5 data is missing. In 2021-2022, around 45% is missing, but in 2024 it's only about 5%. There are no embassy measurements for 2026 because the station had already stopped working.

I expected PM2.5 to be worst in the evening, but the average winter daily cycle peaks at 15:00. The lowest point is at 06:00. I checked nearby Clarity sensors, and they showed the same pattern.

Maybe daytime winds carry polluted air uphill from the lower parts of the city. I haven't confirmed that explanation yet.

## Day 4

I made the first plots in `01_eda.ipynb`. Winter PM2.5 is about 6 times higher than in summer. The average is around 70 µg/m³ in January and 67 in December, compared with 10-12 in summer.

During the heating season, weekdays and weekends look almost the same. Both average around 50-55 µg/m³. Traffic might not be the main cause of winter smog, but this comparison doesn't prove it.

The 10 most polluted days were all in December or January, between 2020 and 2023. Daily averages were 170-222 µg/m³. Temperatures were between -14 and -6 °C, and the boundary layer was only about 25-70 m high. With less air to mix into, pollution could build up near the ground.

The wind wasn't always weak on those days. Cold weather and poor air mixing may explain more than wind speed alone.

## Day 5

I compared daily PM2.5 with the weather. The strongest correlation was with temperature at -0.65, followed by boundary layer height, or BLH, at -0.51. Wind speed had almost no correlation at 0.03.

BLH tells us how high the air can mix. When it's low, pollution can stay trapped near the ground. The median line on the plot also shows lower PM2.5 as BLH gets higher.

I also checked what happened around the start of heating, roughly 15 October. PM2.5 went from 25 to 31 µg/m³ in 2020, from 14 to 20 in 2023, and from 18 to 31 in 2025. The change was small in 2022 and 2024. There wasn't enough data around this period for the same comparison in 2021.

PM2.5 often went up around the start of heating. It also gets colder around then, so the increase may not be from heating alone.

## Day 6

I compared CAMS forecasts with measured PM2.5. In winter, from December to February, CAMS averaged about 34 µg/m³ while the measurements averaged 61. The bias was -27 µg/m³, and the mean absolute error, or MAE, was about 40.

Most winter points on the scatter plot were below the red line. CAMS often predicted much lower PM2.5 than was actually measured.

In summer, the forecasts were much closer. The MAE was about 6 µg/m³. CAMS was a little too high on average, with a bias of +3 µg/m³.

The biggest errors were in winter, when Almaty has its worst smog. That's where I want my model to improve the forecasts most.

## Day 7

I wrote what I learned in the notebook and updated the README. I added two things about the data: the time zone change in March 2024 and missing BLH data for January-June 2024. I also added two plots to the README: PM2.5 by month and the daily cycle.

## Day 8

I made features.py to turn hourly data into one row per day with 38 features. The model predicts tomorrow's average PM2.5 using data available by midnight. The strongest feature is PM2.5 at 23:00 today, which makes sense because bad air late at night often carries over into the next day.

Tomorrow's weather comes from actual recorded data, so it works like a perfect forecast. Real forecasts can be wrong, so the results may look better than they would in practice.
## Day 9

I made evaluate.py. It calculates MAE, RMSE and how often the model gets the air quality category right (good, unhealthy or very unhealthy).

I split the data by time: train is September 2020 - 2023, validation is 2024 and test is 2025. I can't shuffle the days, because then the model would see days from the future and the results would look better than they really are.

At first I wanted to test on 2026, but the embassy station stopped working on 14 November 2025. So the test year is 2025.

The simplest baseline is "tomorrow = today". It got an MAE of 8.83 µg/m³ on the test year. CAMS got 10.19, so even this simple guess is more accurate than CAMS for Almaty
## Day 10

I made train.py and compared four forecasts on the 2025 test data. CAMS got MAE 10.19 µg/m³, linear regression 9.66, the baseline 8.83 and LightGBM 6.84.

LightGBM did best in this run. Its MAE was about 33% lower than CAMS and 23% lower than the baseline. It also got the PM2.5 group right on about 92% of test days.

Linear regression did worse than just saying "tomorrow = today". Maybe it misses how cold weather, wind and heating work together. The scores alone don't tell me why it did worse.

I used early stopping to choose how many trees to use. It stops training when the validation score stops improving, which helps reduce overfitting. Then I trained LightGBM again on train + validation with the same number of trees, so the final model could also use 2024, the year just before the test.
