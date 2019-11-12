struct string_double_pair{
  1 : string key
  2 : double value
}

service CalcServer {
    list<double> word_distance(1: list<list<string>> word_pairs)
    list<i32> get_sentence_neighbors(1: i32 id, 2: i32 n)
    list<string_double_pair> get_synonyms(1: string word)
    list<list<string_double_pair>> get_multi_synonyms(1: string word, 2: i32 n)
}
