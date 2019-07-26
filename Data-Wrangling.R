library(dragracer)
library(tidyverse)
library(lubridate)

############################
## DATA LOADING ############
############################
setwd('/Users/justinpimentel/Desktop/Drag Race Project/Data')

queens <- dragracer::rpdr_contestants %>% 
                    mutate(dob = ymd(dob),
                    season = gsub('^(S|S0)','',season))
write.csv(queens,'Queens.csv', row.names = FALSE)
## Run Web-Scraping.py after writing 'Queens.csv'

social <- read.csv('Social-Media-With-Followers.csv') %>% 
                    mutate_if(is.factor, as.character) %>%
                    mutate(Twitter = ifelse(Twitter == "", NA, Twitter))

write.csv(dragracer::rpdr_contep, 'originalEpisodeData.csv', row.names = FALSE)

queenFullData <- queens %>% 
                    left_join(social, by = c("contestant" = "Queen"))



##############################
## ASTROLOGY DATA ############
##############################

getSign = function(birthday){
  for(sign in astrology){
    if (birthday %within% sign$astrologyInterval){
      return(sign$astrologySign)
    }
  }
}

queenBirthdays = queens %>% select(contestant, dob) %>% distinct()
astrology = list(list(astrologyInterval = interval(ymd("2000-03-21"), ymd("2000-04-19")), astrologySign = 'Aries'),
                 list(astrologyInterval = interval(ymd("2000-04-20"), ymd("2000-05-20")), astrologySign = 'Taurus'),
                 list(astrologyInterval = interval(ymd("2000-05-21"), ymd("2000-06-20")), astrologySign = 'Gemini'),
                 list(astrologyInterval = interval(ymd("2000-06-21"), ymd("2000-07-22")), astrologySign = 'Cancer'),
                 list(astrologyInterval = interval(ymd("2000-07-23"), ymd("2000-08-22")), astrologySign = 'Leo'),
                 list(astrologyInterval = interval(ymd("2000-08-23"), ymd("2000-09-22")), astrologySign = 'Virgo'),
                 list(astrologyInterval = interval(ymd("2000-09-23"), ymd("2000-10-22")), astrologySign = 'Libra'),
                 list(astrologyInterval = interval(ymd("2000-10-23"), ymd("2000-11-21")), astrologySign = 'Scorpio'),
                 list(astrologyInterval = interval(ymd("2000-11-22"), ymd("2000-12-21")), astrologySign = 'Sagittarius'),
                 list(astrologyInterval = interval(ymd("2000-12-22"), ymd("2000-12-31")), astrologySign = 'Capricorn'),
                 list(astrologyInterval = interval(ymd("2001-01-01"), ymd("2001-01-19")), astrologySign = 'Capricorn'),
                 list(astrologyInterval = interval(ymd("2001-01-20"), ymd("2001-02-18")), astrologySign = 'Aquarius'),
                 list(astrologyInterval = interval(ymd("2001-02-19"), ymd("2001-03-20")), astrologySign = 'Pisces'))

newYearBool = grepl('....-(0[1-2]-[0-3][0-9])|(03-(([0-1][0-9])|(20)))', queenBirthdays$dob)
queenBirthdays$dob[newYearBool] <- gsub('^....-','2001-',queenBirthdays$dob[newYearBool])
queenBirthdays$dob[!newYearBool] <- gsub('^....-','2000-',queenBirthdays$dob[!newYearBool])
queenBirthdays$`Astrology Sign` <- sapply(queenBirthdays$dob, function(x) getSign(x))

queenFullData <- queenFullData %>% 
                      left_join(queenBirthdays %>% 
                      select(contestant, `Astrology Sign`), by = "contestant")

write.csv(queenFullData,'Queen Full Data.csv', row.names = FALSE)
###############################
## DB SCORE PER EP ############
###############################
fixedEp <- dragracer::rpdr_contep %>%
            left_join(dragracer::rpdr_ep %>% select(season, episode, special)) %>%
            dplyr::filter(participant == 1, special == 0) %>%
            select(season,episode,contestant,everything(),-special, -participant) %>%
            mutate(season = as.numeric(gsub('^(S|S0)','',season)),
                   outcome = ifelse(outcome %in% c('WIN+RTRN','WIN'), 2,
                                    ifelse(outcome == 'HIGH',1,
                                           ifelse(outcome %in% c('SAFE+DEPT','SAFE'),0,
                                                  ifelse(outcome == 'LOW',-1,
                                                         ifelse(outcome == 'BTM',-2,'Other')))))) %>%
            dplyr::filter(outcome != 'Other') %>% 
            mutate_at(vars('outcome','eliminated'), as.numeric) %>%
            group_by(season,contestant) %>%
            arrange(season,episode) %>%
            mutate(cumSum = cumsum(outcome),
                   episode = row_number(),
                   lastEp = max(episode)) %>% ungroup()

write.csv(fixedEp, 'Corrected Episodes.csv', row.names = FALSE)




## Outcome data with ELIM
outcomeData <- fixedEp %>% select(season, contestant, outcome, eliminated) %>% 
                            dplyr::filter(eliminated == 1) %>%
                            mutate(outcome = ifelse(eliminated == 1, -5, eliminated)) %>%
                            bind_rows(fixedEp %>% select(season,contestant,outcome,eliminated))
                          
write.csv(outcomeData, 'outcomeData.csv', row.names = FALSE)
