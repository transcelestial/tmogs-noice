import csv

extracted_list = []

# with open('harris/corner_coords_2022-11-16 15:37:46.862401.csv', 'r') as file:
#     data = csv.reader(file, delimiter = '[')
#     next(data)

#     for row in data:
#         row_content = row[0].lstrip('[(').rstrip(')]')
#         pos = row_content.split(',')
#         pos[0] = int(pos[0])
#         pos[1] = int(pos[1])
#         extracted_list.append(pos)
#     print(extracted_list[0][0])
#     print(type(extracted_list[0][0]))

with open('harris/subpixel_coords_2022-11-16 15:37:46.862401.csv', 'r') as file:
    data = csv.reader(file, delimiter = '[')
    next(data)

    for row in data:
        row_content = row[1].lstrip('(').rstrip(')')
        pos = row_content.split(', ')
        pos[0] = int(pos[0])
        pos[1] = int(pos[1])
        extracted_list.append(pos)
    print(extracted_list[0][0])
    print(type(extracted_list[0][0]))