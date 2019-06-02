import { AzureFunction, Context, HttpRequest } from '@azure/functions';
import RegattaCentral from './regattaCentral';
import RowingEvent from './rowingEvent';
import BritishRowing from './britishRowing';
import { DateTime } from 'luxon';
import { setSidebar } from './reddit';

const index: AzureFunction = async function() {
  let events: RowingEvent[] = [];

  events = events.concat(await RegattaCentral.events());
  events = events.concat(await BritishRowing.events());

  events = filterEvents(events);

  const markdownTable = generateTable(events);

  await setSidebar(markdownTable);
};

const filterEvents = (events: RowingEvent[]): RowingEvent[] =>
  events
    .filter(
      event =>
        event.date >= DateTime.local() &&
        event.date <= DateTime.local().plus({ days: 7 })
    )
    .sort((a, b) => a.date.valueOf() - b.date.valueOf());

const generateTable = (events: RowingEvent[]): string =>
  '**Upcoming Races**\n\n|**Race**|**Date**|**Venue**|\n|-|-|-|\n'.concat(
    events.map(event => event.tableRow()).join('')
  );

export default index;
