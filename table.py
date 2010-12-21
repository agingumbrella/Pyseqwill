import common
import tables
import data

class GenomeWindow(tables.IsDescription):
    chr = tables.Int8Col()
    start = tables.Int32Col()
    end = tables.Int32Col()
    omp_mk4 = tables.Int32Col()
    ngn_mk4 = tables.Int32Col()
    omp_hmedip = tables.Int32Col()
    ngn_hmedip = tables.Int32Col()
    icam_hmedip = tables.Int32Col() 

class Chromosome:
    def __init__(self, tab, chr):
        self.tab = tab
        self.chr = common.CHR_TO_NUM[chr]
        self.coverage = [r for r in self.tab.readWhere("chr == %d" % self.chr)]
        sorted(self.coverage, key=lambda x: x["start"])
    

def load_seq_data():
    f = tables.openFile(common.DATA_PATH+"all_data.h5", mode="r")
    return f.root.seqdata.windows

def import_seq_data():
    f = create_seq_table()
    tab = f.root.seqdata.windows
    load_data_into_seq_table(tab)

def create_seq_table():
    h5file = tables.openFile(common.DATA_PATH+"all_data.h5", mode="w", title="hme and chip data")
    group = h5file.createGroup("/", "seqdata", 'Seq data')
    tab = h5file.createTable(group, 'windows', GenomeWindow, "Sliding windows across genome")
    return h5file
     
def load_data_into_seq_table(tab):
    window = tab.row
    genome = data.Genome("/gpfs/runtime/bioinfo/bowtie/indexes/mm9_all_folded_with_chrID.fa")
    print "Loaded genome"
    omp_mk4 = data.Coverage(common.DATA_PATH+"omp_mk4.bam", genome)
    print "Loaded omp mk4"
    ngn_mk4 = data.Coverage(common.DATA_PATH+"ngn_mk4.bam", genome)
    print "Loaded ngn mk4"
    omp_hmedip = data.Coverage(common.DATA_PATH+"omp_hmedip.bam",genome)
    print "Loaded omp hmedip"
    ngn_hmedip = data.Coverage(common.DATA_PATH+"ngn_hmedip.bam",genome)
    print "Loaded ngn hmedip"
    icam_hmedip = data.Coverage(common.DATA_PATH+"icam_hmedip.bam",genome)
    print "Loaded icam hmedip"
    parts = genome.partition(common.WINDOW_SIZE)
    for chr, rngs in parts.iteritems():
        chr_idx = common.CHR_TO_NUM[chr]
        i = 0
        for rng in rngs:
            window['chr'] = chr_idx
            window['start'] = rng[0]
            window['end'] = rng[1]
            window['omp_mk4'] = omp_mk4.pileup[chr][i]
            window['ngn_mk4'] = ngn_mk4.pileup[chr][i]
            window['omp_hmedip'] = omp_hmedip.pileup[chr][i]
            window['ngn_hmedip'] = ngn_hmedip.pileup[chr][i]
            window['icam_hmedip'] = icam_hmedip.pileup[chr][i]
            i += 1
            window.append()
    tab.flush()
