lexicon array #arr_size ( shape_block -- total_cells ) "Computes the total flat cell capacity needed to back a multidimensional shape layout configuration array."
lexicon array #arr_make ( shape_block -- ptr ) "Allocates a new N-dimensional heap array with inline metadata tracking shape ranks and dimensions. Returns an opaque pointer token."
lexicon array #arr_offset ( ptr coords_block -- flat_offset ) "Maps a coordinates index block into a flat linear integer memory offset relative to the base heap pointer address."
lexicon array #arr_get ( ptr coords_block -- val ) "Retrieves a scalar or object value from an N-dimensional heap array using an explicit coordinates indexing block."
lexicon array #arr_set ( val ptr coords_block -- ) "Writes a scalar or object value into an N-dimensional heap array at the specific position dictated by a coordinates block."

lexicon list #lst_make ( initial_capacity -- ptr ) "Allocates a growable, mutable list structure tracking capacity, length, and a distinct sub-allocated flat data segment pointer."
lexicon list #lst_get ( ptr idx -- val ) "Performs a 0-indexed cell lookup inside a growable list structure pointer."
lexicon list #lst_set ( val ptr idx -- ) "Overwrites a cell value inside a growable list structure at a targeted 0-indexed integer slot."
lexicon list #lst_push ( val ptr -- ) "Appends an element to a growable list, updating length integers. Automatically manages vector expansion tracking constraints."

lexicon map #map_make ( buckets_size -- ptr ) "Allocates a flat key-value hash map array backed by a dedicated bucket structure layout."
lexicon map #map_get ( ptr key -- val ) "Queries a hash map structure via integer offsets for an explicit key identifier match. Returns the associated payload value, or -1 on miss."
lexicon map #map_set ( val ptr key -- ) "Inserts or updates a key-value pair inside a hash map structure using safe integer offsets relative to the base heap pointer."

lexicon record #rec_make ( size -- ptr ) "Allocates a fixed-capacity record memory segment on the heap containing a specific number of data slots."
lexicon record #rec_get ( ptr field_offset -- val ) "Reads an encapsulated record field entry from a constant integer offset cell."
lexicon record #rec_set ( val ptr field_offset -- ) "Writes an encapsulated record field entry into a constant integer offset cell."
