import { AzureFunction, Context } from '@azure/functions';
import axios from 'axios';
import axiosRetry from 'axios-retry';
import * as cheerio from 'cheerio';
import iconv from 'iconv-lite';

axiosRetry(axios, { retries: 3 });

const index: AzureFunction = async function(
  context: Context,
  msg: string
): Promise<string[]> {
  const data = iconv.decode(
    await (await axios.get(msg, { responseType: 'arraybuffer' })).data,
    'windows1252'
  );
  const $ = cheerio.load(data);
  const category = $('h2')
    .first()
    .text();
  return await $('.list')
    .map((_, element) => {
      const $ = cheerio.load(element);
      if ($('b').text() !== '') {
        return {
          name: $('b').text(),
          category: category.replace(':', ''),
          location: $('i')
            .text()
            .slice(3),
          src: new URL($('img').attr('src'), msg).pathname.slice(8)
        };
      }
    })
    .get();
};

export default index;
