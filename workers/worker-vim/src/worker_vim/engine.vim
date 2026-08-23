" OpenRegex Vim engine driver.
"
" Reads a request from $OPENREGEX_IN, matches it against a scratch buffer and
" writes the byte offsets of every match to $OPENREGEX_OUT.
"
" Matching happens in a buffer rather than against a String on purpose: Vim
" patterns are buffer-oriented, so ^ and $ mean start and end of line, \%^ and
" \%$ mean start and end of file, and a pattern may span lines with \n. Running
" match() over a String with a moving start offset would make ^ match at every
" restart position, which is not what a Vim user sees.

function! s:CharBytes(line, col) abort
  let l:rest = strpart(a:line, a:col - 1)
  if l:rest ==# ''
    return 1
  endif
  return strlen(strcharpart(l:rest, 0, 1))
endfunction

function! s:Collect(request) abort
  let l:pattern = a:request.regex
  let l:limit = a:request.max_matches
  let l:lines = split(a:request.text, "\n", 1)

  enew!
  setlocal buftype=nofile bufhidden=hide noswapfile
  call setline(1, l:lines)

  " Byte offset of the first character of every line, newline included.
  let l:offsets = []
  let l:running = 0
  for l:line in l:lines
    call add(l:offsets, l:running)
    let l:running += strlen(l:line) + 1
  endfor

  let l:matches = []
  call cursor(1, 1)
  let l:flags = 'cW'

  while len(l:matches) < l:limit
    let l:start = searchpos(l:pattern, l:flags)
    if l:start[0] == 0
      break
    endif

    call cursor(l:start[0], l:start[1])
    let l:finish = searchpos(l:pattern, 'ceW')

    let l:start_offset = l:offsets[l:start[0] - 1] + l:start[1] - 1

    if l:finish[0] == 0 || l:finish[0] < l:start[0]
          \ || (l:finish[0] == l:start[0] && l:finish[1] < l:start[1])
      " Zero-width match: 'e' has nothing to move onto.
      let l:end_offset = l:start_offset
      call cursor(l:start[0], l:start[1])
    else
      let l:width = s:CharBytes(getline(l:finish[0]), l:finish[1])
      let l:end_offset = l:offsets[l:finish[0] - 1] + l:finish[1] - 1 + l:width
      call cursor(l:finish[0], l:finish[1])
    endif

    call add(l:matches, [l:start_offset, l:end_offset])

    " Without 'c' the next search starts one character past the cursor, which
    " is exactly where the following non-overlapping match may begin.
    let l:flags = 'W'
  endwhile

  return l:matches
endfunction

function! s:Main() abort
  let l:payload = {}
  try
    let l:request = json_decode(join(readfile($OPENREGEX_IN), ''))
    let l:payload = {'matches': s:Collect(l:request)}
  catch
    let l:payload = {'error': v:exception}
  endtry
  call writefile([json_encode(l:payload)], $OPENREGEX_OUT)
endfunction

call s:Main()
qall!
