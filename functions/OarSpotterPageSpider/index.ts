import { AzureFunction, HttpRequest, Context } from '@azure/functions';
import axios from 'axios';
import axiosRetry from 'axios-retry';
import * as cheerio from 'cheerio';

axiosRetry(axios, { retries: 3 });

const baseUrl = 'http://www.oarspotter.com';
let seenUrls: string[] = [];

const index: AzureFunction = async function(): Promise<string[]> {
  return await extractLinks(baseUrl);
};

const extractLinks = async (url: string): Promise<string[]> => {
  seenUrls.push(url);
  const data = await (await axios.get(url)).data;
  const $ = cheerio.load(data);
  return (await Promise.all(
    $(`a[href^='${baseUrl}/blades']`)
      .map(async (_, element) => {
        let pages: string[] = [element.attribs['href']];
        const link = element.attribs['href'];
        if (!seenUrls.includes(link) && link.startsWith(baseUrl)) {
          pages = pages.concat(await extractLinks(link));
        }
        return pages;
      })
      .get()
  )).reduce((x, y) => x.concat(y), []);
};

export default index;
