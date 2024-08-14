from tokenize import String


def countLetters(s):
    i = 0
    let_map = {}
    while i < len(s):
        letter = s[i]
        if '(' == s[i]:
            i += 1
            sub_map, increase = countLetters(s[i:])
            i += increase
            for let in sub_map:
                if let_map.get(let):
                    let_map[let] += sub_map[let]
                else:
                    let_map[let] = sub_map[let]
            continue
        if ')' == letter:
            multiplier = 0
            multiple = 1
            while i < len(s) - 1:
                i += 1
                if s[i].isdigit():
                    multiplier += int(s[i]) * multiple
                    multiple *= 10
                else:
                    i -= 1
                    break
            if multiplier == 0:
                multiplier = 1
            for let in let_map:
                let_map[let] *= multiplier
            return let_map, i + 1
        count = 0
        multiple = 1
        while i < len(s) - 1:
            i += 1
            if s[i].isdigit():
                count += int(s[i]) * multiple
                multiple *= 10
            else:
                i -= 1
                break
        if count == 0:
            count = 1
        if let_map.get(letter):
            let_map[letter] += count
        else:
            let_map[letter] = count
        i += 1
    return let_map


if __name__ == '__main__':
    while True:
        string = input()
        if 'q' == string:
            break
        res = ''
        letters = ''
        letter_map = countLetters(string)
        for letter in letter_map:
            letters += letter
        sort_string = sorted(letters)
        for letter in sort_string:
            res += letter + str(letter_map[letter])
        print(res)