import { ASTNode } from '../../../core/types';

export const buildRegexTree = (regex: string): ASTNode => {
  let groupId = 1;
  let pos = 0;
  const root: ASTNode = { type: 'root', children: [], startIndex: 0 };
  const stack: ASTNode[] = [root];

  while (pos < regex.length) {
    const char = regex[pos];
    const current = stack[stack.length - 1];

    if (regex.startsWith('(*', pos)) {
      const end = regex.indexOf(')', pos);
      if (end !== -1) {
         current.children!.push({ type: 'text', text: regex.substring(pos, end + 1), startIndex: pos, endIndex: end + 1 });
         pos = end + 1;
         continue;
      }
    }

    if (char === '\\') {
      let len = 2;
      if (pos + 1 < regex.length) {
        const next = regex[pos + 1];
        if (next === 'p' || next === 'P' || next === 'b' || next === 'k' || next === 'g') {
          if (regex[pos + 2] === '{' || regex[pos + 2] === '<') {
            const closeChar = regex[pos + 2] === '{' ? '}' : '>';
            let end = pos + 3;
            while (end < regex.length && regex[end] !== closeChar) end++;
            if (end < regex.length) len = end - pos + 1;
          }
        } else if (next === 'x') {
          if (regex[pos + 2] === '{') {
            let end = pos + 3;
            while (end < regex.length && regex[end] !== '}') end++;
            if (end < regex.length) len = end - pos + 1;
          } else {
            len = Math.min(regex.length - pos, 4);
          }
        } else if (next === 'u') {
          len = Math.min(regex.length - pos, 6);
        } else if (next === 'U') {
          len = Math.min(regex.length - pos, 10);
        } else if (/[0-9]/.test(next)) {
          let end = pos + 1;
          while (end < pos + 4 && end < regex.length && /[0-9]/.test(regex[end])) end++;
          len = end - pos;
        }
      }
      current.children!.push({ type: 'text', text: regex.substring(pos, pos + len), startIndex: pos, endIndex: pos + len });
      pos += len;
    } else if (char === '[') {
      let end = pos + 1;
      let inPosix = false;
      while (end < regex.length) {
        if (regex.startsWith('[:', end)) {
          inPosix = true;
          end += 2;
        } else if (inPosix && regex.startsWith(':]', end)) {
          inPosix = false;
          end += 2;
        } else if (regex[end] === '\\') {
          end += 2;
        } else if (regex[end] === ']' && !inPosix) {
          end++;
          break;
        } else {
          end++;
        }
      }
      current.children!.push({ type: 'text', text: regex.substring(pos, end), startIndex: pos, endIndex: end });
      pos = end;
    } else if (char === '(') {
      let isCapturing = true;
      let prefix = '(';
      let i = pos + 1;

      if (regex.startsWith('?', i)) {
        const match = regex.substring(pos).match(/^\(\?(?:P?<[^>]+>|'[a-zA-Z0-9_-]+'|<[=!]|<!|<=|[=!:>|~]|R|\&[a-zA-Z0-9_-]+|-?[a-zA-Z]+\:?|\([^\)]+\))/);
        if (match) {
          prefix = match[0];
          i = pos + prefix.length;
          if (!prefix.includes('<') && !prefix.includes("'") && !prefix.match(/^\(\?[0-9R\&]/)) {
            isCapturing = false;
          }
        } else {
          let closeParen = regex.indexOf(')', i);
          if (closeParen !== -1) {
            current.children!.push({ type: 'text', text: regex.substring(pos, closeParen + 1), startIndex: pos, endIndex: closeParen + 1 });
            pos = closeParen + 1;
            continue;
          }
        }
      }

      const node: ASTNode = {
        type: 'group',
        isCapturing,
        id: isCapturing ? groupId++ : undefined,
        children: [{ type: 'text', text: prefix, startIndex: pos, endIndex: i }],
        startIndex: pos
      };
      current.children!.push(node);
      stack.push(node);
      pos = i;
    } else if (char === ')') {
      if (stack.length > 1) {
        const node = stack.pop()!;
        node.children!.push({ type: 'text', text: ')', startIndex: pos, endIndex: pos + 1 });
        node.endIndex = pos + 1;
      } else {
        current.children!.push({ type: 'text', text: ')', startIndex: pos, endIndex: pos + 1 });
      }
      pos++;
    } else if (char === '{') {
      let end = pos + 1;
      while (end < regex.length && regex[end] !== '}') {
        end++;
      }
      if (end < regex.length && regex[end] === '}') {
        let nextPos = end + 1;
        if (nextPos < regex.length && (regex[nextPos] === '?' || regex[nextPos] === '+')) {
          nextPos++;
        }
        current.children!.push({ type: 'text', text: regex.substring(pos, nextPos), startIndex: pos, endIndex: nextPos });
        pos = nextPos;
      } else {
        current.children!.push({ type: 'text', text: char, startIndex: pos, endIndex: pos + 1 });
        pos++;
      }
    } else if (char === '*' || char === '+' || char === '?') {
      let nextPos = pos + 1;
      if (nextPos < regex.length && (regex[nextPos] === '?' || regex[nextPos] === '+')) {
        nextPos++;
      }
      current.children!.push({ type: 'text', text: regex.substring(pos, nextPos), startIndex: pos, endIndex: nextPos });
      pos = nextPos;
    } else {
      current.children!.push({ type: 'text', text: char, startIndex: pos, endIndex: pos + 1 });
      pos++;
    }
  }

  while (stack.length > 1) {
    const node = stack.pop()!;
    node.endIndex = regex.length;
  }
  root.endIndex = regex.length;

  return root;
};