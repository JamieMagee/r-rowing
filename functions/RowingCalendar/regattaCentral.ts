import axios, { AxiosResponse } from 'axios';
import RowingEvent from './rowingEvent';
import { DateTime } from 'luxon';

class RegattaCentral {
  static readonly COUNTRIES: string[] = [
    'AU',
    'CA',
    'DE',
    'IT',
    'US',
    'DK',
    'HK',
    'IE',
    'NO',
    'SI'
  ];

  static async events(): Promise<RowingEvent[]> {
    return (await Promise.all(
      RegattaCentral.COUNTRIES.map(async country => {
        const response = await axios.get(
          `https://www.regattacentral.com/v3/regattas/jobs?resultsOnly=false&country=${country}&state=all&year=0&type=all`
        );
        return RegattaCentral.parse(response);
      })
    )).reduce((x, y) => x.concat(y));
  }

  static parse(res: AxiosResponse): RowingEvent[] {
    return res.data.data.map(eventJson => {
      return new RowingEvent({
        name: eventJson.full_name,
        date: DateTime.fromISO(eventJson.startDate, { zone: 'utc' }).startOf(
          'day'
        ),
        link: `https://www.regattacentral.com/regatta/?job_id=${
          eventJson.job_id
        }`,
        location: eventJson.location
      });
    });
  }
}

export default RegattaCentral;
