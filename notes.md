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
