import { DateTime } from 'luxon';

class RowingEvent {
  name: string;
  date?: DateTime;
  link?: string;
  location?: string;

  public constructor(init?: Partial<RowingEvent>) {
    Object.assign(this, init);
  }

  tableRow() {
    return `|[${this.name}](${this.link})|${this.date.toFormat('dd MMMM')}|${
      this.location
    }|\n`;
  }
}

export default RowingEvent;
