import options
from pes import * 

class Avg_PES(PES):
    """ Avg potential energy surface calculators """

    def __init__(self,
            PES1,
            PES2):
        self.PES1 = PES1
        self.PES2 = PES2
        self.lot = PES1.lot

    @staticmethod
    def from_options(**kwargs):
        """ Returns an instance of this class with default options updated from values in kwargs"""
        return Avg_PES(Avg_PES.default_options().set_values(kwargs))

    def get_energy(self,geom):
        if self.PES1.multiplicity==self.PES2.multiplicity:
            assert self.PES2.ad_idx>self.PES1.ad_idx,"dgrad wrong direction"
        self.dE = self.PES2.get_energy(geom) - self.PES1.get_energy(geom)
        return 0.5*(self.PES1.get_energy(geom) + self.PES2.get_energy(geom))

    def get_gradient(self,geom):
        return 0.5*(self.PES1.get_gradient(geom) + self.PES2.get_gradient(geom))

    def get_coupling(self,geom):
        assert self.PES1.multiplicity==self.PES2.multiplicity,"coupling is 0"
        assert self.PES1.ad_idx!=self.PES2.ad_idx,"coupling is 0"
        return self.lot.get_coupling(geom,self.PES1.multiplicity,self.PES1.ad_idx,self.PES2.ad_idx)

    def get_dgrad(self,geom):
        if self.PES1.multiplicity==self.PES2.multiplicity:
            assert self.PES2.ad_idx>self.PES1.ad_idx,"dgrad wrong direction"
        return (self.PES2.get_gradient(geom) - self.PES1.get_gradient(geom))

if __name__ == '__main__':

    import pybel as pb    
    import manage_xyz
    from dlc import *
    from molpro import *

    if False:
        filepath="tests/fluoroethene.xyz"
        nocc=10
        nactive=2
    if True:
        filepath="tests/twisted_ethene.xyz"
        nocc=6
        nactive=4
    geom=manage_xyz.read_xyz(filepath,scale=1)   
    lot=Molpro.from_options(states=[(1,0),(1,1)],charge=0,nocc=nocc,nactive=nactive,basis='6-31G*',do_coupling=True,nproc=4)
    # PES object
    pes = PES.from_options(lot=lot,ad_idx=0,multiplicity=1)
    mol1=pb.readfile("xyz",filepath).next()
    isOkay = mol1.OBMol.AddBond(6,4,1)
    pes1 = PES.from_options(lot=lot,ad_idx=0,multiplicity=1)
    pes2 = PES.from_options(lot=lot,ad_idx=1,multiplicity=1)
    p = Avg_PES(pes1,pes2)
    ic1=DLC.from_options(mol=mol1,PES=p)

    dvec = ic1.PES.get_coupling(geom)
    dgrad = ic1.PES.get_dgrad(geom)

    print "Ut"
    print ic1.Ut
    dvecq = ic1.grad_to_q(dvec)
    dgradq = ic1.grad_to_q(dgrad)
    print "dgradq,dvecq"
    print dgradq.T
    print dvecq.T
    dvecq_U = ic1.fromDLC_to_ICbasis(dvecq)
    dgradq_U = ic1.fromDLC_to_ICbasis(dgradq)
    print "dgradq_U,dvecq_U"
    print dgradq_U.T
    print dvecq_U.T

    constraints = np.zeros((len(dvecq_U),2),dtype=float)
    constraints[:,0] = dvecq_U[:,0]
    constraints[:,1] = dgradq_U[:,0]
    ic1.opt_constraint2(constraints)
    print ic1.Ut
    ic1.bmat_create()
    print ic1.q


