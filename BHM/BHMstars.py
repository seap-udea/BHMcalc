###################################################
#  ____  _    _ __  __           _      
# |  _ \| |  | |  \/  |         | |     
# | |_) | |__| | \  / | ___ __ _| | ___ 
# |  _ <|  __  | |\/| |/ __/ _` | |/ __|
# | |_) | |  | | |  | | (_| (_| | | (__ 
# |____/|_|  |_|_|  |_|\___\__,_|_|\___|
# v2.0
###################################################
# 2014 [)] Jorge I. Zuluaga, Viva la BHM!
###################################################
# Stellar evolution routines
###################################################
from BHM import *
from BHM.BHMnum import *

###################################################
#PACKAGES
###################################################

###################################################
#CONFIGURATION
###################################################
ZSVEC_DEF="ZSVEC_siblings"
NTIMES=100

###################################################
#MACROS
###################################################
RHO_COL=1
TEFF_COL=2
RAD_COL=3
LUM_COL=4

###################################################
#GLOBALS
###################################################
SMset=[]
Zset=[]
SMglob=dict2obj(dict())
ZSVEC_full=np.array([
        0.0001,0.0002,0.0004,0.0006,0.0008,
        0.0010,0.0020,0.0030,0.0040,0.0050,0.0060,0.0070,0.0080,0.0090,
        0.0100,0.0125,0.0150,0.0175,
        0.0200,0.0225,0.0250,0.0275,
        0.0300,0.0325,0.0350,0.0375,
        0.0400,0.0425,0.0450,0.0475,
        0.0500,0.0525,0.0550,0.0575,
        0.0600
        ])
ZSVEC_coarse=np.array([0.0001,0.0010,0.0050,0.0100,0.0152,0.0200,0.0300,0.0400,0.0500,0.0600])
ZSVEC_siblings=np.array([0.0100,0.0152,0.0200])
ZSVEC_solar=np.array([0.0152])

###################################################
#ROUTINES
###################################################
def chooseZsvec(Z,zsdef=ZSVEC_DEF):
    ZSs=["ZSVEC_siblings","ZSVEC_coarse","ZSVEC_full"]
    qoutdef=False;qoutoth=False
    #if Z==ZSVEC_solar[0]:zsvec="ZSVEC_solar"
    if False:pass
    else:
        zsvec=zsdef
        for ZS in ZSs:
            exec("Zvec=%s[%s==Z]"%(ZS,ZS))
            if len(Zvec)>0:
                zsvec=ZS
                qoutdef=False
                break                
            exec("lzsvec=len(%s)"%(ZS))
            exec("lzgrea=len(%s[%s>Z])"%(ZS,ZS))
            if lzgrea==0 or lzgrea==lzsvec:
                if ZS==zsdef:
                    qoutdef=True
            else:
                qoutoth=True
                zsvecoth=ZS
    if qoutdef:
        if qoutoth:zsvec=zsvecoth
        else:
            PRINTERR("No isochrone found for Z = %.5f"%(Z))
            errorCode("DATA_ERROR")
    return zsvec

def PropertySet(Ms,age,prop,iiso):
    if age<0:return -1
    global SMset

    SMiso=SMset[iiso]
    age=np.log10(age*1E9)
    id=np.arange(0,SMiso.nAges)
    iage=id[SMiso.Ages==age]
    
    if len(iage):
        iage=iage[0]
        try:
            p=eval("SMiso.%sint[iage](Ms)"%prop)
        except:
            p=-1
    else:
        lages=id[SMiso.Ages<=age]
        gages=id[SMiso.Ages>age]

        try:
            iless=lages[-1]
            igreat=gages[0]
            t1=SMiso.Ages[iless]
            t2=SMiso.Ages[igreat]
            try:
                p1=eval("SMiso.%sint[iless](Ms)"%prop)
                p2=eval("SMiso.%sint[igreat](Ms)"%prop)
                p=p1+(p2-p1)/(t2-t1)*(age-t1)
            except:
                p=-1
        except:
            p=-1

    return p

def StellarPropertyNorm(prop,Z,Ms,tau,norm=True):
    val=StellarProperty(prop,Z,Ms,tau)
    if not norm:return val
    if prop=='Temperature':
        val=(val-SMglob.Tsun)+TSUN
    elif prop=='Radius':
        val=(val/SMglob.Rsun)
    elif prop=='Luminosity':
        val=(val/SMglob.Lsun)
    return val

def StellarProperty(prop,Z,Ms,tau):
    global SMset
    num=len(SMset)
    ps=[]
    Zs=[]
    for i in xrange(0,num):
        Zi=Zset[i]
        exec "p=SMset[i].%s(Ms,tau)"%prop in globals(),locals()
        if p==-1:
            #print "Property '%s' calculated at Z = %f, Ms = %f, tau = %f is null"%(prop,Zi,Ms,tau)
            pass
        else:
            Zs+=[Zi]
            ps+=[p]
    try:
        func=interp1d(Zs,ps,kind='slinear')
        val=func(Z)
    except:
        #print "Metallicity Z = %f is out of range"%Z
        val=-1.2345
        #exit(1)
    return val

def loadIsochroneSet(Zs=ZSVEC_full,
                     verbose=False):
    global SMset,Zset
    Zset=Zs

    if verbose:print "Loading isochrone set..."
    iiso=0
    for Z in Zs:
        if verbose:print "\tLoading Isochrone for Z = %f..."%Z
        SMiso=dict2obj(dict())
        Stars='BHM/data/Stars/Padova-Z%.4f.dat'%Z
        Mmin=0.1
        Mmax=2.0
        try:
            data=np.loadtxt(Stars)
        except IOError:
            print "Error openning file '%s'"%Stars
            exit(1)
        ndata=data.shape[0]
        idata=np.arange(0,ndata)

        SMiso.Ages=[]
        ageold=data[0,1]
        for datum in data:
            age=datum[1]
            if age>ageold:
                SMiso.Ages+=[ageold]
                ageold=age
        SMiso.Ages+=[ageold]
        SMiso.nAges=len(SMiso.Ages)
        SMiso.Ages=np.array(SMiso.Ages)
        SMiso.tmin=10**SMiso.Ages[0]/1E9
        SMiso.tmax=10**SMiso.Ages[-1]/1E9
    
        SMiso.Msvec=[]
        SMiso.Mrvec=[]
        SMiso.Lsvec=[]
        SMiso.Rsvec=[]
        SMiso.Tsvec=[]
        SMiso.Mbolvec=[]
        SMiso.logLsvec=[]
        SMiso.loggsvec=[]
        SMiso.logTsvec=[]

        SMiso.Mrint=[]
        SMiso.Lsint=[]
        SMiso.Rsint=[]
        SMiso.Tsint=[]
        SMiso.Mbolint=[]
        SMiso.logLsint=[]
        SMiso.loggsint=[]
        SMiso.logTsint=[]

        Filters=['U','B','V','R','I','J','H','K']
        for filter in Filters:
            exec "SMiso.%svec=[]"%filter in globals(),locals()
            exec "SMiso.%sint=[]"%filter in globals(),locals()

        SMiso.Mmin=1E100
        SMiso.Mmax=0

        it=0
        for age in SMiso.Ages:
            ages=data[:,1]
            sages=ages==age
            ies=idata[sages]
            nies=ies.shape[0]
            masses=data[sages,2]
            nmass=masses.shape[0]
            imass=np.arange(0,nmass)
            bmass=masses>=Mmin
            iselbot=imass[bmass]
            tmass=masses<=Mmax
            iseltop=imass[tmass]
            
            ini=ies[0]+iselbot[0]
            end=ies[0]+iseltop[-1]
            
            Ms=data[ini:end,2]
            SMiso.Msvec+=[Ms]
            
            SMiso.Mrvec+=[data[ini:end,3]]
            SMiso.Mrint+=[interp1d(SMiso.Msvec[it],SMiso.Mrvec[it],kind='slinear')]

            SMiso.Lsvec+=[10**data[ini:end,4]]
            SMiso.Lsint+=[interp1d(SMiso.Msvec[it],SMiso.Lsvec[it],kind='slinear')]

            SMiso.logLsvec+=[data[ini:end,4]]
            SMiso.logLsint+=[interp1d(SMiso.Msvec[it],SMiso.logLsvec[it],kind='slinear')]

            SMiso.Tsvec+=[10**data[ini:end,5]]
            SMiso.Tsint+=[interp1d(SMiso.Msvec[it],SMiso.Tsvec[it],kind='slinear')]

            SMiso.logTsvec+=[data[ini:end,5]]
            SMiso.logTsint+=[interp1d(SMiso.Msvec[it],SMiso.logTsvec[it],kind='slinear')]

            SMiso.loggsvec+=[data[ini:end,6]]
            SMiso.loggsint+=[interp1d(SMiso.Msvec[it],SMiso.loggsvec[it],kind='slinear')]

            gs=10**data[ini:end,6]/100
            SMiso.Rsvec+=[np.sqrt(GCONST*(Ms*MSUN)/gs)/RSUN]
            SMiso.Rsint+=[interp1d(SMiso.Msvec[it],SMiso.Rsvec[it],kind='slinear')]

            SMiso.Mbolvec+=[data[ini:end,7]]
            SMiso.Mbolint+=[interp1d(SMiso.Msvec[it],SMiso.Mbolvec[it],kind='slinear')]

            col=8
            for filter in Filters:
                exec "SMiso.%svec+=[data[ini:end,%d]]"%(filter,col) in globals(),locals()
                exec "SMiso.%sint+=[interp1d(SMiso.Msvec[it],SMiso.%svec[it],kind='slinear')]"%(filter,
                                                                                     filter) in globals(),locals()
                col+=1

            SMiso.Mmin=min(SMiso.Mmin,min(Ms))
            SMiso.Mmax=max(SMiso.Mmax,max(Ms))
        
            it+=1

        SMset+=[SMiso]
        exec "SMset[iiso].Mactual=lambda M,t:PropertySet(M,t,'Mr',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].Luminosity=lambda M,t:PropertySet(M,t,'Ls',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].logLuminosity=lambda M,t:PropertySet(M,t,'logLs',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].Radius=lambda M,t:PropertySet(M,t,'Rs',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].logGravitation=lambda M,t:PropertySet(M,t,'loggs',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].Temperature=lambda M,t:PropertySet(M,t,'Ts',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].logTemperature=lambda M,t:PropertySet(M,t,'logTs',%d)"%iiso in globals(),locals()
        exec "SMset[iiso].Mbol=lambda M,t:PropertySet(M,t,'Mbol',%d)"%iiso in globals(),locals()
        for filter in Filters:
            exec "SMset[iiso].%s=lambda M,t:PropertySet(M,t,'%s',%d)"%(filter,
                                                                       filter,
                                                                       iiso) in globals(),locals()
        iiso+=1

    return iiso

def StellarRadius(Ms,gs):
    from numpy import sqrt
    Rs=sqrt(GCONST*Ms*MSUN/gs)/RSUN
    return Rs

def StellarGTRL(Z,M,t):
    logg=StellarProperty('logGravitation',Z,M,t)
    g=10**logg/100
    R=StellarRadius(M,g)
    logT=StellarProperty('logTemperature',Z,M,t)
    T=10**logT
    logL=StellarProperty('logLuminosity',Z,M,t)
    L=10**logL
    if logg==-1.2345:g=-1
    if logT==-1.2345:T=-1
    if logL==-1.2345:L=-1
    return g,T,R,L

def minmaxRadius(Z,M,tmin=TAU_MIN,tmax=1.0):
    Rmin=1E100
    Rmax=0.0
    for t in np.linspace(tmin,tmax,20):
        g,T,R,L=StellarGTRL(Z,M,t)
        if R>Rmax:Rmax=R
        if R<Rmin:Rmin=R
    return Rmin,Rmax

def XYfromZ(Z):
    """
    See: http://stev.oapd.inaf.it/cgi-bin/cmd
    """
    Y=0.2485+1.78*Z
    X=1-Y-Z
    return X,Y

XSUN,YSUN=XYfromZ(ZSUN)
    
#METALLICITY FROM Z
def FeH2Z(FeH,X=0.75,A=1.0):
    """
    Values at sun.txt
    
    Examples:
    print FeH2Z(-0.5,X=0.75,A=0.9)
    print FeH2Z(-0.5,X=0.70,A=1.0)
    print FeH2Z(-0.5,X=0.75,A=1.0)
    print FeH2Z(-0.5,X=0.70,A=0.9)
    """
    """
    Wikipedia
    XSun=0.7110
    ZSun=0.0149
    YSun=0.2741
    """
    Z=ZSUN*(X/XSUN)*10**(A*FeH)
    return Z

#CALCULATE Z FROM METALLICITY
def ZfromFHe(FeH):
    """
    Example:
    print ZfromFHe(-0.55)
    print ZfromFHe(-0.40)
    """
    Xvec=np.linspace(0.700,0.739,100)
    Avec=np.linspace(0.9,1.0,100)
    Zvals=[]
    for X in Xvec:
        for A in Avec:
            Zvals+=[FeH2Z(FeH,X=X,A=A)]
    Z=np.mean(Zvals)
    dZ=np.std(Zvals)
    return Z,dZ

def FeHfromZ(Z):
    func=lambda FeH:ZfromFHe(FeH)[0]-Z
    FeH=bisectFunction(func,-10.0,10.0)
    return FeH

def evoFunctions(evodata):
    ts=evodata[:,0]
    logrho_func=interp1d(np.log10(ts),
                      np.log10(evodata[:,RHO_COL]),
                      kind='slinear')
    Teff_func=interp1d(np.log10(ts),
                       evodata[:,TEFF_COL],
                       kind='slinear')
    logR_func=interp1d(np.log10(ts),
                    np.log10(evodata[:,RAD_COL]),
                    kind='slinear')
    logL_func=interp1d(np.log10(ts),
                       np.log10(evodata[:,LUM_COL]),
                       kind='slinear')
    return logrho_func,Teff_func,logR_func,logL_func

###################################################
#TEST
###################################################
if __name__=="__main__":
    num=loadIsochroneSet(Zs=ZSVEC_siblings,verbose=True)

    Ms=1.0
    tau=TAGE
    Z=0.0152
    
    Ls=StellarProperty('Luminosity',Z,Ms,tau)
    Lslog=10**StellarProperty('logLuminosity',Z,Ms,tau)
    print "Ls (normal) = %e"%Ls
    print "Ls (log-interp) = %e"%Lslog
    
    Rs=StellarProperty('Radius',Z,Ms,tau)
    loggs=StellarProperty('logGravitation',Z,Ms,tau)
    gs=10**loggs/100
    Rslog=np.sqrt(GCONST*Ms*MSUN/gs)/RSUN
    print "Rs (normal) = %e"%Rs
    print "Rs (log-interp g) = %e"%Rslog
    
    Ts=StellarProperty('Temperature',Z,Ms,tau)
    Tslog=10**StellarProperty('logTemperature',Z,Ms,tau)
    print "Ts (normal) = %e"%Ts
    print "Ts (log-interp) = %e"%Tslog

def Seff2014(Teff,crits=['recent venus'],Tsun=TSUN,Mp='1.0'):
    """
    Kopparapu et al., 2014
    """
    
    if Teff<2600:Teff=2600.0
    if Teff>7200:Teff=7200.0
    Tst=Teff-Tsun

    Seffs=[]
    for crit in crits:
        if crit=="runaway greenhouse":
            if Mp=='1.0':
                S=1.107
                a=1.332E-4;b=1.58E-8;c=-8.308E-12;d=-1.931E-15
            if Mp=='5.0':
                S=1.188
                a=1.433E-4;b=1.707E-8;c=-8.968E-12;d=-2.048E-15
            if Mp=='0.1':
                S=0.99
                a=1.209E-4;b=1.404E-8;c=-7.418E-12;d=-1.713E-15
        elif crit=="moist greenhouse":
            S=1.0146
            #SAME AS 2013
            a=8.1884E-5;b=1.9394E-9;c=-4.3618E-12;d=-6.8260E-16
        elif crit=="recent venus":
            #ALL MASSES ARE EQUARL
            S=1.776
            a=2.136E-4;b=2.533E-8;c=-1.332E-11;d=-3.097E-15
        elif crit=="maximum greenhouse":
            S=0.356
            a=6.171E-5;b=1.698E-9;c=-3.198E-12;d=-5.575E-16
        elif crit=="early mars":
            S=0.32
            a=5.547E-5;b=1.526E-9;c=-2.874E-12;d=-5.011E-16
        else:
            S=a=b=c=d=Tst=-1
        Seffs+=[S+a*Tst+b*Tst**2+c*Tst**3+d*Tst**4]
        
    if len(Seffs)==1:return Seffs[0]
    else:return Seffs

def HZ(Ls,Teff,lin='recent venus',lout='early mars',Seff=Seff2014):
    """
    Habitable Zone limits by Kopparapu et al. (2013)
    Ls: In solar Units
    Teff: In K
    """
    if Ls<0 or Teff<0:
        raise Exception("Negative value in stellar properties")
    Seffin,Seffout=Seff(Teff,crits=[lin,lout])
    Seffsun=1.0
    lin=(Ls/Seffin)**0.5
    lout=(Ls/Seffout)**0.5
    aHZ=(Ls/Seffsun)**0.5
    return lin,aHZ,lout

"""
Taken from Claret & Gimenez (1989, 1990)
ZAMS values
"""
STELLAR_MOI=np.array([
        [0.020,0.230**1],
        [0.600,0.378**2],
        [0.800,0.323**2],
        [1.000,0.277**2],
        [1.122,0.248**2],
        [1.259,0.224**2],
        ])
def stellarMoI(M,type="Regression"):
    """
    #type=Regression,Upper,Lower
    plt.figure()
    plt.plot(STELLAR_MOI[:,0],sqrt(STELLAR_MOI[:,1]))
    plt.savefig("moi.png")
    print sqrt(stellarMoI(1.5))
    exit(0)
    """    
    #Regression Coefficients (calculated at May.7/2013)
    a=-1.577705e-01
    b=2.339366e-01
    
    #Lower limit
    MoIlow=0.076729 #Claret & Gimenez (1989)

    #Upper limit
    MoIup=0.25 #Leconte et al. (2011)
    
    #type="Upper"
    if type=="Regression":
        MoI=a*M+b
    elif type=="Upper":
        MoI=MoIup
    else:
        MoI=MoIlow

    if M>STELLAR_MOI[-1,0]:
        MoI=STELLAR_MOI[-1,-1]

    return MoI

def dissipationTime(M,R,L):
    #Zahn (2008) DISSIPATION TIME
    tdiss=3.48*((M*MSUN*(R*RSUN)**2)/(L*LSUN))**(1./3)    
    return tdiss

def Flux(q,Ls1=1.0,Ls2=1.0,rc1=0.1,rc2=0.1,D=1.0,qsgn=1):
    R1=np.sqrt(D**2+rc1**2+2*D*rc1*np.sin(q))
    R2=np.sqrt(D**2+rc2**2-2*D*rc2*np.sin(q))
    F=qsgn*(Ls1/R1**2+Ls2/R2**2)
    return F

def AverageFlux(d,**args):
    args['D']=d
    intFlux=lambda x:Flux(x,**args)
    #print args
    F=integrate(intFlux,0.0,2*PI)[0]/(2*PI)
    #print F
    #exit(0)
    return F

def HZbin(q,Ls1,Ls2,Teffbin,abin,
          Seff=Seff2014,
          crits=['recent venus','early mars']):

    rc2=abin/(q+1)
    rc1=q*rc2
    args=dict(Ls1=Ls1,Ls2=Ls2,rc1=rc1,rc2=rc2)

    #EFFECTIVE FLUXES
    Seffin,Seffout=Seff(Teffbin,crits=crits)

    #INNER LIMIT
    AF=lambda x:AverageFlux(x,**args)-Seffin
    lin=bisectFunction(AF,1.0)
    #lin=bisectFunction(AF,1E-4,20)

    #OUTER LIMIT
    AF=lambda x:AverageFlux(x,**args)-Seffout
    lout=bisectFunction(AF,1E-4,20)

    aHZ=(lin+lout)/2

    return lin,aHZ,lout
