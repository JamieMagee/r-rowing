import * as cheerio from 'cheerio';
import axios from 'axios';
import RowingEvent from './rowingEvent';
import { DateTime } from 'luxon';

class BritishRowing {
  static readonly url: string =
    'https://www.britishrowing.org/rowing-activity-finder/calendar/?type=competitions';

  static async events(): Promise<RowingEvent[]> {
    const res = await axios.get(BritishRowing.url);
    const data = await res.data;
    const $ = cheerio.load(data);
    return $('.rich-results__result__content')
      .map((_, element) => {
        return new RowingEvent({
          name: cheerio
            .load(element)('h3')
            .text(),
          date: DateTime.fromFormat(
            cheerio
              .load(element)('time')
              .text()
              .replace(/(\d{1,2})[a-z]{2}\b/i, ''),
            'EEEE d of MMMM yyyy',
            { zone: 'utc' }
          ).startOf('day')
        });
      })
      .get();
  }
}

export default BritishRowing;
