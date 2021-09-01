

export class EventBodyItem {
  'newValues': Array<Date>;
  'oldValues': Array<string>;
  'property': string;

    private static discriminator: string | undefined = undefined;

    private static attributeTypeMap: Array<{name: string, baseName: string, type: string}> = [
        {
            "name": "newValues",
            "baseName": "newValues",
            "type": "Array<Date>"
        },
        {
            "name": "oldValues",
            "baseName": "oldValues",
            "type": "Array<string>"
        },
        {
            "name": "property",
            "baseName": "property",
            "type": "string"
        }    ];

    public static getAttributeTypeMap() {
        return EventBodyItem.attributeTypeMap;
    }
}




